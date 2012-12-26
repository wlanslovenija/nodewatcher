
def register(model, permission, description):
    """
    Dynamically adds a new permission into an existing model.
    """
    # Prevent double registration of permissions
    for existing_perm, _ in model._meta.permissions:
        if existing_perm == permission:
            return

    model._meta.permissions.append((permission, description))
