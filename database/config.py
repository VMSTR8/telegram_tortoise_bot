from settings.settings import DATABASE_URL

TORTOISE_ORM = {
    'connections': {'default': DATABASE_URL},
    'apps': {
        'models': {
            'models': ['database.user.models', 'aerich.models'],
            'default_connections': 'default'
        },
    },
}
