FROM python:3.8

WORKDIR /app

COPY requirements_production.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./april /app
COPY ./config /app
COPY ./sidewinder /app
COPY ./templates /app

# TODO: Might not keep this. External management thing instead?
COPY ./manage.py /app

CMD ["uvicorn", "sidewinder.asgi:application"]
