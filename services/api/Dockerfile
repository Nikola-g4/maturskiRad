FROM python:3.9.5-buster

WORKDIR /usr/src/app

ADD ./requirements.txt /usr/src/app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD . /usr/src/app

EXPOSE 5000

CMD gunicorn --worker-class eventlet -w 1 --log-level DEBUG --bind 0.0.0.0:5000 wsgi:app
