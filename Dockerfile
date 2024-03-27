FROM python:3.11.2-alpine3.17
WORKDIR /app
ADD requirements.txt /app
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories\
    && apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev bash\
    && apk add --no-cache libffi openssl subversion
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple\
    && pip3 install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple\
    && apk del .build-deps
ADD . /app
RUN rm -f /etc/localtime
RUN  ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' > /etc/timezone
CMD uvicorn main:app --host 0.0.0.0 --port 8000
EXPOSE 8000
