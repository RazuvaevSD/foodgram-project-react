FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r ./backend/foodgram/requirements.txt --no-cache-dir

COPY ./backend/foodgram/ ./

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]