FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app
WORKDIR /app
COPY . .

RUN pip install -U pip
RUN pip install -r requirements.txt