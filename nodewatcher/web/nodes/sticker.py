from django.template import Context, loader
from django.contrib.sites.models import Site
from django.conf import settings
import subprocess, os

def generate_sticker(user, regenerate = False):
  """
  A helper method for generating a PDF sticker.

  @param user: A valid User instance
  """
  url_base = "%s://%s" % ('https' if getattr(settings, 'FEEDS_USE_HTTPS', None) else 'http', Site.objects.get_current().domain)
  
  if user.info_sticker and not regenerate:
    # User already has a sticker generated, just return the path
    return '%s/stickers/sticker-%s.pdf' % (url_base, user.id)

  # Generate one using pdflatex
  t = loader.get_template('nodes/stickers/%s' % user.project.sticker)
  c = Context({
    'name'  : user.name,
    'phone' : user.phone
  })

  f = open('/tmp/tmpsticker-%d.tex' % user.id, 'w')
  f.write(t.render(c).encode('utf8'))
  f.close()

  p = subprocess.Popen(
    [
      "/usr/bin/pdflatex",
      "--output-directory=/var/www/nodes.wlan-lj.net/stickers",
      "--aux-directory=/tmp",
      "--interaction=nonstopmode",
      "--jobname=sticker-%s" % user.id,
      "/tmp/tmpsticker-%d.tex" % user.id
    ],
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE
  )
  p.communicate()
  os.unlink('/tmp/tmpsticker-%d.tex' % user.id)

  # Mark sticker as generated
  user.info_sticker = True
  user.save()

  return '%s/stickers/sticker-%s.pdf' % (user.id, url_base)

