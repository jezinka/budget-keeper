FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY auth/ /auth/
COPY logs/ /logs/
COPY src/ /src/
RUN ls -la /src/*

CMD ["python3", "/src/main.py"]