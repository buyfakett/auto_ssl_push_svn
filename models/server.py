from tortoise.models import Model
from tortoise import fields


class Server(Model):
    id = fields.IntField(pk=True)
    webroot = fields.CharField(max_length=255, description="SVN路径")
    hostname = fields.CharField(max_length=50, description="Server hostname")
