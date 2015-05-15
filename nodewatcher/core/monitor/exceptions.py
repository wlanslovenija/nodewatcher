

class NodeProcessorAbort(Exception):
    """
    This exception should be raised by node processors when they wish to abort any
    further processing for the current node. Cleanup handler for the current
    processor and all previous processors will still run.

    Raising this exceptio will NOT rollback the transaction.
    """

    pass
