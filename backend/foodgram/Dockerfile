FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt --no-cache-dir

COPY ./ ./

RUN mkdir -p ./foodgram/static/data/

COPY ../data/ ./foodgram/static/data/

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]