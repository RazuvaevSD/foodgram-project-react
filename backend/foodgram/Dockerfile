FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt --no-cache-dir

COPY ./ ./
COPY ../data/ ./foodgram/static/data/

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8090"]