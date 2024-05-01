# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/13 15:35
from pyconfig_util.config_util import setting

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': str(setting.DATABASE_HOST),
                'port': str(setting.DATABASE_PORT),
                'user': str(setting.DATABASE_USER),
                'password': str(setting.DATABASE_PASSWORD),
                'database': str(setting.DATABASE_DATABASE),
            }
        }
    },
    'apps': {
        'models': {
            'models': ['aerich.models', 'models.first_domain', 'models.server', 'models.ssl', 'models.user'],
            'default_connection': 'default',
        }
    },
}
