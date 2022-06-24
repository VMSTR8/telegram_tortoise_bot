from tortoise.validators import Validator
from tortoise.exceptions import ValidationError


class EmptyValueValidator(Validator):
    def __call__(self, value: str):
        if value == '':
            raise ValidationError(f"Value '{value}' can't be empty!")
