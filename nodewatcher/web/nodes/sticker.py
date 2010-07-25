import subprocess, os

from django.template import Context, loader
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.contrib.auth import forms

username_regex = forms.UserCreationForm.base_fields['username'].regex

def generate_sticker(user, regenerate = False):
  """
  A helper method for generating a PDF sticker.

  @param user: A valid User instance
  """
  
  # Filter out invalid characters to be sure
  sticker_name = filter(lambda x: username_regex.match(x), user.user.username)

  if not getattr(settings, 'STICKERS_ENABLED', None) or not sticker_name:
    return reverse('my_sticker')
  
  if user.info_sticker and not regenerate:
    # User already has a sticker generated, just return the path
    return '%sstickers/sticker-%s.pdf' % (settings.MEDIA_URL, sticker_name)
  
  # Autodetect pdflatex location
  PDFLATEX_LOCATIONS = [
    getattr(settings, 'PDFLATEX_BIN', None),
    '/usr/bin/pdflatex',
    '/sw/bin/pdflatex'
  ]
  for pdflatex_loc in PDFLATEX_LOCATIONS:
    if not pdflatex_loc:
      continue
    if os.path.isfile(pdflatex_loc):
      break
  else:
    raise ImproperlyConfigured("Could not find pdflatex executable.")
  
  # Generate one using pdflatex
  t = loader.get_template('nodes/stickers/%s' % (user.project.sticker or 'default.tex'))
  c = Context({
    'name'    : user.name,
    'phone'   : user.phone,
    'network' : { 'name'        : settings.NETWORK_NAME,
                  'home'        : settings.NETWORK_HOME,
                  'contact'     : settings.NETWORK_CONTACT,
                  'description' : getattr(settings, 'NETWORK_DESCRIPTION', None)
                },
  })

  tmp_dir = getattr(settings, 'STICKERS_TEMP_DIR', '/tmp/')
  tmp_sticker = '%stmpsticker-%s.tex' % (tmp_dir, sticker_name)

  f = open(tmp_sticker, 'w')
  f.write(t.render(c).encode('utf8'))
  f.close()

  p = subprocess.Popen(
    [
      pdflatex_loc,
      "--output-directory=%s" % settings.STICKERS_DIR,
      "--aux-directory=%s" % tmp_dir,
      "--interaction=nonstopmode",
      "--jobname=sticker-%s" % sticker_name,
      tmp_sticker
    ],
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE
  )
  p.communicate()
  os.unlink(tmp_sticker)

  # Mark sticker as generated
  user.info_sticker = True
  user.save()

  return '%sstickers/sticker-%s.pdf' % (settings.MEDIA_URL, sticker_name)
