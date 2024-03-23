FROM python:3.8-slim-buster
ENV TZ="Europe/Warsaw"

WORKDIR /app
ADD init/rabbitmq.conf /etc/rabbitmq/
ADD init/definitions.json /etc/rabbitmq/
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY auth/ auth/
COPY src/ src/
RUN mkdir logs

CMD ["python3", "src/main.py"]
