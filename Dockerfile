FROM python:3.11.2
ADD . /app
WORKDIR /app
RUN pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN rm -f /etc/localtime
RUN  ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' > /etc/timezone
CMD uvicorn main:app --reload
EXPOSE 8000