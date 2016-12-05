from django import dispatch

# Called to extract a processing context from HTTP headers. The returned contexts
# are merged together.
extract_context = dispatch.Signal(providing_args=['headers', 'uuid'])
