from django.db import transaction
from django.utils import timezone

from . import models


@transaction.atomic(savepoint=False)
def verify_identity(node, mechanism, data):
    """
    Performs identity verification and takes actions based on the configured
    policy. If the verification succeeds, this function returns True.

    :param node: Node instance
    :param mechanism: A subclass of IdentityMechanismConfig that should be used
    :param data: Mechanism-specific data
    :return: True if verification succeeded, False otherwise
    """

    if not issubclass(mechanism, models.IdentityMechanismConfig):
        raise TypeError("Passed identity mechanism class must be a subclass of IdentityMechanismConfig.")

    # If node is not defined, verification fails.
    if not node:
        return False

    # Fetch the identity configuration so we know what is the policy.
    config = node.config.core.identity()
    if not config:
        return False

    # Go through the list of trusted identities and try to match one to the passed data.
    matched_trusted = False
    matched_untrusted = False
    for identity in node.config.core.identity.mechanisms(onlyclass=mechanism):
        if identity.is_match(data):
            # Update last seen timestamp.
            identity.last_seen = timezone.now()
            identity.save()

            if identity.trusted:
                matched_trusted = True
            else:
                matched_untrusted = True

    if not matched_trusted:
        # If nothing matched, check whether we should store the identity.
        is_first_use = False
        if config.trust_policy == 'first':
            # When the configured policy is trust on first use, we check whether there are
            # currently no other identities configured.
            is_first_use = not node.config.core.identity.mechanisms().exists()

        if not matched_untrusted and (config.store_unknown or is_first_use):
            kwargs = mechanism.from_data(data)
            if kwargs is not None:
                kwargs.update({
                    'identity': config,
                    'trusted': is_first_use,
                    'automatically_added': True,
                    'last_seen': timezone.now(),
                })

                identity = node.config.core.identity.mechanisms(create=mechanism, **kwargs)
                identity.save()

                # When the configured policy is trust on first use, we trust this identity.
                if is_first_use:
                    return True

                # Ensure that only one untrusted automatically added identity is stored.
                node.config.core.identity.mechanisms(onlyclass=mechanism).filter(
                    trusted=False,
                    automatically_added=True,
                ).exclude(pk=identity.pk).delete()
            else:
                # Failed to decode data with the target mechanism.
                pass

    # We trust any identity in case of the 'any' policy.
    if config.trust_policy == 'any':
        return True

    return matched_trusted
