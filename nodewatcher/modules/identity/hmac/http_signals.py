import base64

from django import dispatch

from nodewatcher.modules.monitor.sources.http import signals


@dispatch.receiver(signals.extract_context)
def http_extract_context(sender, headers, uuid, **kwargs):
    # Decode the Base64-encoded signature.
    try:
        data = headers.get('HTTP_X_NODEWATCHER_SIGNATURE', None)
        data = base64.b64decode(data)
    except TypeError:
        data = None

    return {
        'identity': {
            'signature': {
                'algorithm': headers.get('HTTP_X_NODEWATCHER_SIGNATURE_ALGORITHM', 'hmac-sha256'),
                'data': data,
            }
        }
    }
