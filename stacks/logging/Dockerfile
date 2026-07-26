FROM python:3.11
WORKDIR /app
COPY config.json /app/config.json
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "logging.py"]
