from django import dispatch

# Called before background firmware build is initiated.
pre_firmware_build = dispatch.Signal(providing_args = ['node', 'platform', 'cfg'])

# Called after the firmware has been built and output files have been saved to
# file storage. If the build process fails, this signal is not emitted.
#
# The files variable contains a list of filenames that have been saved to the
# specified file storage which is held by the storage argument. If filenames
# are modified, the list MUST be modified as well.
post_firmware_build = dispatch.Signal(providing_args = ['node', 'platform', 'cfg', 'files', 'storage'])

# Called after build succeeds and post_firmware_build handlers have been called
finalize_firmware_build = dispatch.Signal(providing_args = ['node', 'platform', 'cfg', 'files', 'storage'])

# Called if the firmware build fails.
fail_firmware_build = dispatch.Signal(providing_args = ['node', 'platform', 'cfg'])
