from tortoise.models import Model
from tortoise import fields


class Ssl(Model):
    id = fields.IntField(pk=True)
    first_domain_id = fields.IntField(description="一级域名id", null=True)
    server_id = fields.IntField(description="服务器id", is_null=False)
    certificate_domain = fields.CharField(max_length=255, description="证书域名")
    webroot = fields.CharField(max_length=255, description="SVN路径")
    register_time = fields.DateField(description="证书注册时间", null=True)
    exp_time = fields.DateField(description="证书到期时间", null=True)
    status = fields.IntField(description="证书状态 0-不进行续期，1-正常，2-过期")

