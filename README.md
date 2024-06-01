# auto_ssl_push_svn

这是一个自动获取/续期ssl证书的服务，并推送到svn

- 需要先添加主域名(目前只支持阿里)
- 然后再添加服务器(svn地址)
- 最后添加要申请证书的域名(每天11点刷新，也可手动刷新)

### 技术

- fastapi

- tortoise-orm

### 使用教程

在项目下的config目录下新建`config.yaml`,并配置，然后运行

#### `config.yaml`模板
```yaml
database:
  host: 0.0.0.0
  port: 5432
  user: postgres
  password: xxx
  database: auto_ssl_push_svn
config:
  token_private_key: xxx
  differ_day: 7
svn:
  user: xxx
  passwd: xxx
  mail: xxx@outlook.com
server:
  host: 0.0.0.0
  password: xxx
push:
  type: ding
  ding_access_token: xxx
cron:
  hour: 11
  minute: 0
```

#### 启动文件
```bash
docker run -id \
--name auto_ssl_push_svn \
-v ./config/:/app/config/ \
-v /etc/letsencrypt:/etc/letsencrypt \
-v ./temp/:/app/temp/ \
-p 8006:8000 \
buyfakett/auto_ssl_push_svn
```

### 支持

1. 【Star】他，让他看到你是爱他的；

2. 【Watching】他，时刻感知他的动态；

3. 【Fork】他，为他增加新功能，修Bug，让他更加卡哇伊；

4. 【Issue】他，告诉他有哪些小脾气，他会改的，手动小绵羊；

5. 【打赏】他，为他买jk；

### 贡献指南

在develop分支上修改或者新开一个分支

### 其他

代码不是很成熟，有bug请及时在github反馈哦~ 或者发作者邮箱：buyfakett@vip.qq.com

觉得作者写的不错的话可以支持一下作者，请作者喝一杯咖啡哦~

| 微信                             | 支付宝                        |
| -------------------------------- | ----------------------------- |
| ![alipay](./pay_img/wechat.webp) | ![wechat](./pay_img/ali.webp) |