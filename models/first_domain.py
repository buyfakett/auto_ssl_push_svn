from tortoise.models import Model
from tortoise import fields


class domain(Model):
    id = fields.IntField(pk=True)
    domain = fields.CharField(max_length=255, description="域名")
    domain_manufacturer = fields.CharField(max_length=50, description="域名厂商")
    domain_account_key = fields.CharField(max_length=100, description="域名厂商子账号key")
    domain_account_secret = fields.CharField(max_length=100, description="域名厂商子账号secret")
    is_delete = fields.BooleanField(default=0, description="是否删除 0-删除，1-不删除")