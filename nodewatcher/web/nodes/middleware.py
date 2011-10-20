import os

class HttpsMiddleware(object):
  """
  This is a dangerous middleware. Use only if your site is behind a proxy which uses only HTTPS outside and you
  want Django to know this. If this is not the case and it is possible to access the site also through HTTP, using
  this middleware could open security holes.
  """

  def process_request(self, request):
    os.environ['HTTPS'] = 'on'
    if hasattr(request, '_req'):
      # ModPython
      request._req.subprocess_env['HTTPS'] = 'on'
    if hasattr(request, 'environ'):
      # WSGI
      request.environ['wsgi.url_scheme'] = 'https'
    return None
