import hashlib
import io
import json
import os

import unidecode

from celery.task import task as celery_task

from django.core.files import uploadedfile
from django import db
from django.db import transaction

from ....utils import loader

from . import signals, base as cgm_base, exceptions
from .. import models as generator_models
from .. import events as generator_events


@celery_task(bind=True)
@transaction.atomic
def background_build(self, result_uuid):
    """
    A task for deferred building of a firmware image.

    :param result_uuid: Destination build result UUID
    """

    result = generator_models.BuildResult.objects.get(pk=result_uuid)
    if result.status != generator_models.BuildResult.PENDING:
        return

    # Try to lock the builder for building
    try:
        generator_models.Builder.objects.select_for_update(nowait=True).filter(pk=result.builder.pk)
    except db.DatabaseError:
        # Retry the build task again in 15 seconds
        raise self.retry(countdown=15)

    result.status = generator_models.BuildResult.BUILDING
    result.save()

    # Ensure that all CGMs are loaded before doing processing
    loader.load_modules('cgm')
    platform = cgm_base.get_platform(result.builder.platform)

    # Dispatch pre-build signal
    signals.pre_firmware_build.send(sender=None, result=result)

    # Build the firmware and obtain firmware files
    try:
        files = platform.build(result)
    except exceptions.BuildError, e:
        if len(e.args) > 0:
            error_message = 'ERROR: %s' % e.args[0]

            if result.build_log:
                result.build_log += '\n' + error_message
            else:
                result.build_log = error_message

        result.status = generator_models.BuildResult.FAILED
        result.save()

        # Dispatch error signal
        signals.fail_firmware_build.send(sender=None, result=result)
        # Dispatch the result failed event
        generator_events.BuildResultFailed(result).post()
        return
    except:
        result.build_log = 'Internal build error.'
        result.status = generator_models.BuildResult.FAILED
        result.save()

        # Dispatch error signal
        signals.fail_firmware_build.send(sender=None, result=result)
        # Dispatch the result failed event
        generator_events.BuildResultFailed(result).post()
        return

    # By default, prepend node name and version before firmware filenames.
    node_name = unidecode.unidecode(result.node.config.core.general().name)
    fw_version = result.builder.version.name.replace('.', '')

    for index, (fw_name, fw_file) in enumerate(files[:]):
        files[index] = ('%s-v%s-%s' % (node_name, fw_version, fw_name), fw_file)

    # Dispatch signal that can be used to modify files
    signals.post_firmware_build.send(sender=None, result=result, files=files)

    # Store resulting files and generate the file manifest.
    manifest = {
        'node': {
            'uuid': str(result.node.uuid),
            'name': node_name,
        },
        'firmware': {
            'version': result.builder.version.name,
        },
        'files': []
    }

    for fw_name, fw_file in files:
        r_file = generator_models.BuildResultFile(
            result=result,
            file=uploadedfile.InMemoryUploadedFile(
                io.BytesIO(fw_file),
                None,
                os.path.basename(fw_name),
                'application/octet-stream',
                len(fw_file),
                None
            ),
            checksum_md5=hashlib.md5(fw_file).hexdigest(),
            checksum_sha256=hashlib.sha256(fw_file).hexdigest(),
        )

        manifest_entry = r_file.to_manifest()
        if manifest_entry is not None:
            manifest['files'].append(manifest_entry)

        r_file.save()

    # Store the manifest.
    manifest = json.dumps(manifest)
    generator_models.BuildResultFile(
        result=result,
        file=uploadedfile.InMemoryUploadedFile(
            io.BytesIO(manifest),
            None,
            'manifest.json',
            'text/json',
            len(manifest),
            None
        ),
        checksum_md5=hashlib.md5(manifest).hexdigest(),
        checksum_sha256=hashlib.sha256(manifest).hexdigest(),
        hidden=True,
    ).save()

    result.status = generator_models.BuildResult.OK
    result.save()

    # Dispatch finalize signal
    signals.finalize_firmware_build.send(sender=None, result=result)
    # Dispatch the result ready event
    generator_events.BuildResultReady(result).post()
