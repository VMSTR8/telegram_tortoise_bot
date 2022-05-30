from tortoise.models import Model
from tortoise import fields


class Team(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, unique=True, null=False)

    def __str__(self):
        return self.title


class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField(unique=True, null=False)
    callsign = fields.CharField(max_length=255, unique=True, null=True)
    is_member = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField(
        'models.Team',
        related_name='users', null=True, on_delete=fields.RESTRICT
    )

    def __str__(self):
        return self.telegram_id


class Location(Model):
    id = fields.IntField(pk=True)
    point = fields.CharField(max_length=255, unique=True, null=False)
    latitude = fields.FloatField(default=00.000000, null=False)
    longitude = fields.FloatField(default=00.000000, null=False)
    team: fields.OneToOneRelation[Team] = fields.OneToOneField(
        'models.Team',
        related_name='locations', null=True, on_delete=fields.RESTRICT
    )

    def __str__(self):
        return self.point
