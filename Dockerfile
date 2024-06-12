FROM node:22 as front-builder
WORKDIR /app
ENV AUTHOR_NAME="buyfakett"
ENV PROJECT_NAME="auto_ssl_push_svn"
RUN git clone https://github.com/${AUTHOR_NAME}/${PROJECT_NAME}_web.git && \
    cd ${PROJECT_NAME}_web && \
    npm i && \
    npm run build
RUN cd ${PROJECT_NAME}_web/ && \
    mv dist web && \
    cd web && \
    mkdir admin/ && \
    mv favicon.ico admin/ && \
    mv index.html admin/ && \
    cd .. && \
    mv web ..

FROM python:3.12.3-alpine3.19 as backend-builder
WORKDIR /app
ADD . .
RUN mkdir web/
COPY --from=front-builder /app/web/ /app/web/

FROM python:3.12.3-alpine3.19 as runner
WORKDIR /app
COPY --from=backend-builder /app/ /app/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel gunicorn \
    && pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev bash \
    && apk add --no-cache libffi openssl subversion \
    && apk del .build-deps
RUN rm -f /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' > /etc/timezone
CMD uvicorn main:app --host 0.0.0.0 --port 8000
EXPOSE 8000
