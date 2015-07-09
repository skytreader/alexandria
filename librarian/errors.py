class ConstraintError(Exception):
    
    def __init__(self, constraint_desc, operation_value):
        self.constraint_desc = constraint_desc
        self.operation_value = operation_value

    def __str__(self):
        return "Not respecting constraint %s given %s." % (str(self.constraint_desc),
          str(self.operation_value))
