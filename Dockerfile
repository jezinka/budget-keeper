FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY auth/ auth/
COPY src/ src/
COPY scripts/ scripts/
RUN mkdir logs

CMD ["python3", "src/main.py"]