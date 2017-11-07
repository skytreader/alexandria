class ConstraintError(Exception):
    """
    When a given constraint in input has been violated.
    """
    
    def __init__(self, constraint_desc, operation_value):
        self.constraint_desc = constraint_desc
        self.operation_value = operation_value

    def __str__(self):
        return "Not respecting constraint %s given %s." % (str(self.constraint_desc),
          str(self.operation_value))

class InvalidRecordState(Exception):
    """
    Throw whenever you think that the records in the database is inconsistent. 
    """

    def __init__(self, record_descriptor):
        self.record_descriptor = record_descriptor

    def __str__(self):
        return "DB record %s violates constraints." % self.record_descriptor
