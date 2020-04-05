FROM python:3.8

WORKDIR /app

COPY requirements* /app
RUN pip install --no-cache-dir -r requirements_production.txt

COPY ./april /app
COPY ./config /app
COPY ./sidewinder /app
COPY ./templates /app

# TODO: Might not keep this. External management thing instead?
COPY ./manage.py /app

CMD ["uvicorn", "sidewinder.asgi:application"]
