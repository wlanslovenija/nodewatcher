import collections

from registry import state as registry_state 

class LazyChoiceList(collections.Sequence):
  def __init__(self):
    super(LazyChoiceList, self).__init__()
    self._list = []
  
  def __len__(self):
    return len(self._list)

  def __getitem__(self, index):
    return self._list[index]
  
  def __nonzero__(self):
    return True

def register_form_for_item(item, form_class):
  """
  Registers a form for use with the specified registry item.
  
  @param item: Registry item class
  @param form_class: Form class
  """
  if not hasattr(item, '_forms'):
    item._forms = {}
  
  item._forms[item] = form_class

def get_registered_choices(choices_id):
  """
  Returns a list of previously registered choices.
  """
  return registry_state.CHOICES_REGISTRY.setdefault(choices_id, LazyChoiceList())

def register_choice(choices_id, enum, text):
  """
  Registers a new choice.
  """
  choices = registry_state.CHOICES_REGISTRY.setdefault(choices_id, LazyChoiceList())._list
  if any([x == enum for x, _ in choices]):
    return
  
  choices.append((enum, text))

