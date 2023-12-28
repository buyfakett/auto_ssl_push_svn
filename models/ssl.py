from tortoise.models import Model
from tortoise import fields


class Ssl(Model):
    id = fields.IntField(pk=True)
    first_domain_id = fields.IntField(description="域名id")
    server_ids = fields.CharField(max_length=25565, description="服务器id组，申请完后需要上传到哪些svn")
    certificate_domain = fields.CharField(max_length=255, description="证书域名")
    register_time = fields.DateField(description="证书注册时间", null=True)
    exp_time = fields.DateField(description="证书到期时间", null=True)
    status = fields.IntField(description="证书状态 0-不进行续期，1-正常，2-新建/过期")

