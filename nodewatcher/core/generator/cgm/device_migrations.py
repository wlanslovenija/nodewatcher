from django.db.migrations.operations import base


class RenameDevice(base.Operation):
    """
    Database migration operation, which updates router device identifiers. It
    should be used when updating device descriptors.
    """

    reduces_to_sql = False
    atomic = True

    def __init__(self, old_id, new_id):
        """
        Constructs a device renaming operation.

        :param old_id: Old device identifier
        :param new_id: New device identifier
        """

        self.old_id = old_id
        self.new_id = new_id
        super(RenameDevice, self).__init__(old_id, new_id)

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        CgmGeneralConfig = from_state.apps.get_model('cgm', 'CgmGeneralConfig')
        CgmGeneralConfig.objects.filter(router=self.old_id).update(router=self.new_id)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        CgmGeneralConfig = from_state.apps.get_model('cgm', 'CgmGeneralConfig')
        CgmGeneralConfig.objects.filter(router=self.new_id).update(router=self.old_id)

    def describe(self):
        return "Rename Device"
