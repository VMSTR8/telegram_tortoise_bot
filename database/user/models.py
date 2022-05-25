from tortoise.models import Model
from tortoise import fields


class Location(Model):
    id = fields.IntField(pk=True)
    point_name = fields.CharField(max_length=255, unique=True)
    point_activation_status = fields.BooleanField(default=False)
    latitude = fields.FloatField()
    longitude = fields.FloatField()

    users: fields.ReverseRelation['User']

    def __str__(self):
        return self.point_name


class User(Model):
    id = fields.IntField(pk=True)
    telegram_user_id = fields.IntField(unique=True)
    callsign = fields.CharField(max_length=255, unique=True, null=True)
    subscribed_date = fields.DatetimeField(auto_now_add=True)
    is_team_member = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)
    locations: fields.ForeignKeyRelation[Location] = fields.ForeignKeyField(
        'models.Location', related_name='users', null=True)

    def __str__(self):
        return self.telegram_user_id
