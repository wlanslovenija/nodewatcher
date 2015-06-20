from django import dispatch

# Called by DnsServerConfigForm to further filter the servers, which are
# contained in server.queryset where server is the underlying form field.
filter_servers = dispatch.Signal(providing_args=['server', 'item', 'cfg', 'request'])
