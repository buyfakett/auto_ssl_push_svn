# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/13 15:35
from tt_util.yaml_util import read_yaml

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': str(read_yaml('host', 'db')),
                'port': str(read_yaml('port', 'db')),
                'user': str(read_yaml('user', 'db')),
                'password': str(read_yaml('password', 'db')),
                'database': str(read_yaml('database', 'db')),
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
