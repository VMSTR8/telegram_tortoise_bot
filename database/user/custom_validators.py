from tortoise.validators import Validator
from tortoise.exceptions import ValidationError


class EmptyValueValidator(Validator):
    """
    Does not allow writing an empty string to the
    database for CharField, TextField.
    """
    def __call__(self, value: str):
        if value == '':
            raise ValidationError("Value can't be empty!")
