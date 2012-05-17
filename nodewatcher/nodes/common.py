from django import forms
from django.db import transaction, connection

class InvalidPluginClass(Exception):
  """
  This exception gets raised when the plugin class does not inherit
  from a predefined superclass.
  """
  pass

def load_plugin(module_path, required_super = None):
  """
  A helper function to load a plugin (class) given its full path
  as a string. Paths are valid Python module names that must be
  importable at time of calling this method.
  
  @param module_path: A valid module path that ends in a class name
  @param required_super: Optional required superclass
  @return: The given class
  """
  module = module_path[0:module_path.rfind('.')]
  className = module_path[module_path.rfind('.') + 1:]
  m = __import__(module, globals(), locals(), [className], -1)
  cls = m.__dict__[className]
  
  if required_super is not None and not issubclass(cls, required_super):
    raise InvalidPluginClass
  
  return cls

class ValidationWarning(Exception):
  pass

class FormWithWarnings(forms.Form):
  """
  A form that adds support for emitting warnings.
  """
  confirm_all_warnings = forms.BooleanField(initial = False, required = False, widget = forms.HiddenInput())
  
  def __init__(self, *args, **kwargs):
    """
    Class constructor.
    """
    super(FormWithWarnings, self).__init__(*args, **kwargs)
    self.warnings = []
    
    # Wrap save method
    old_save = self.save
    def wrapped_save(*args, **kwargs):
      # Check that the database has savepoint support, otherwise this might have
      # unindented consequences of data corruption; in such cases we disable warnings
      if not connection.features.uses_savepoints:
        return old_save(*args, **kwargs)
      
      # First call save normally and if warnings have gone unhandled we
      # raise a ValidationWarning exception
      try:
        sid = transaction.savepoint() 
        res = old_save(*args, **kwargs)
        if len(self.warnings):
          data = self.data.copy()
          data['confirm_all_warnings'] = True
          self.data = data
          raise ValidationWarning
        
        transaction.savepoint_commit(sid)
      except:
        transaction.savepoint_rollback(sid)
        raise
    
    self.save = wrapped_save
   
  def warning_or_continue(self, message):
    """
    Registers a new warning. If the user hasn't confirmed warnings he will
    get the form again.
    """
    if self.cleaned_data.get('confirm_all_warnings', False):
      return
    
    self.warnings.append(message)

