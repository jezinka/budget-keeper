FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY auth/ auth/
COPY src/ src/
COPY scripts/ scripts/
RUN mkdir logs

RUN chmod 0644 src/main.py

#Install Cron
RUN apt-get update
RUN apt-get -y install cron

# Add the cron job
RUN crontab -l | { cat; echo "*/5 * * * * python src/main.py"; } | crontab -

# Run the command on container startup
CMD cron
