FROM python:3.11

WORKDIR /app

COPY config.json /app/config.json
COPY api.py /app/api.py
COPY requirements.txt /app/requirements.txt

COPY crewagent/ /app/crewagent/
COPY rag-agent/ /app/rag-agent/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "api.py"]
