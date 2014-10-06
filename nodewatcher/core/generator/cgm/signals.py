from django import dispatch

# Called before background firmware build is initiated.
pre_firmware_build = dispatch.Signal(providing_args=['result'])

# Called after the firmware has been built and output files have been
# downloaded from the builder. If the build process fails, this signal is
# not emitted.
#
# The files variable contains a list of (name, content) tuples which may
# be replaced or even erased.
post_firmware_build = dispatch.Signal(providing_args=['result', 'files'])

# Called after build succeeds and post_firmware_build handlers have been called
finalize_firmware_build = dispatch.Signal(providing_args=['result'])

# Called if the firmware build fails.
fail_firmware_build = dispatch.Signal(providing_args=['result'])
