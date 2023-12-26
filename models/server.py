from tortoise.models import Model
from tortoise import fields


class Server(Model):
    id = fields.IntField(pk=True)
    ssl_id = fields.IntField(description="证书表id", null=True)
    hostname = fields.CharField(max_length=50, description="Server hostname")
    ip = fields.CharField(max_length=50, description="服务器ip")
    password = fields.CharField(max_length=255, description="服务器密码")
