from tortoise.models import Model
from tortoise import fields
from tortoise.validators import MinValueValidator, MaxValueValidator

from database.user.custom_validators import EmptyValueValidator


class Team(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(
        max_length=255,
        unique=True,
        null=False,
        validators=[EmptyValueValidator()]
    )

    def __str__(self):
        return self.title


class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField(unique=True, null=False)
    callsign = fields.CharField(
        max_length=255,
        unique=True,
        null=True,
        validators=[EmptyValueValidator()]
    )
    is_admin = fields.BooleanField(default=False)
    in_game = fields.BooleanField(default=False)
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField(
        'models.Team',
        related_name='users', null=True, on_delete=fields.SET_NULL
    )

    def __str__(self):
        return self.telegram_id


class Location(Model):
    id = fields.IntField(pk=True)
    point = fields.CharField(
        max_length=255,
        unique=True,
        null=False,
        validators=[EmptyValueValidator()]
    )
    latitude = fields.FloatField(
        default=00.000000,
        null=False,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = fields.FloatField(
        default=00.000000,
        null=False,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    in_game = fields.BooleanField(default=True, null=False)
    time = fields.FloatField(default=1200.0, null=False)
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField(
        'models.Team',
        related_name='locations', null=True, on_delete=fields.SET_NULL
    )

    def __str__(self):
        return self.point
