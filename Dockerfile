FROM python:3.9

ENV PYTHONUNBUFFERED=1


WORKDIR /app

COPY . .
COPY requirements.txt /app/worker_requirements.txt

RUN apt-get update -y && pip install -r requirements.txt

CMD celery --app src.celery_farmer worker --loglevel=info -Q remote_queue -n $WORKER_NAME
