
def register(model, permission, description):
  """
  Dynamically adds a new permission into an existing model.
  """
  model._meta.permissions.append((permission, description))

