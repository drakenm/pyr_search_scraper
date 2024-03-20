# DOCKERFILE
FROM python:3.12-alpine

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./ /code/conf.yaml

CMD ["python", "/code/app/main.py"]