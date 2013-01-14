from django import dispatch

# Called before background firmware build is initiated.
pre_firmware_build = dispatch.Signal(providing_args = ['node', 'platform', 'cfg'])

# Called after the firmware has been built and output files are available,
# but before the files are moved/renamed. If the build process fails, this signal
# is not emitted.
process_firmware_files = dispatch.Signal(providing_args = ['node', 'platform', 'cfg', 'files'])

# Called after the firmware images have been moved.
post_firmware_build = dispatch.Signal(providing_args = ['node', 'platform', 'cfg', 'files'])

# Called if the firmware build fails.
fail_firmware_build = dispatch.Signal(providing_args = ['node', 'platform', 'cfg'])
