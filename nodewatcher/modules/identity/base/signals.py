from django import dispatch

# Called to perform verification using all supported identity mechanisms.
verify = dispatch.Signal(providing_args=['node', 'context'])
