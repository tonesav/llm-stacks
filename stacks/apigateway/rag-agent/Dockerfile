FROM python:3.11

WORKDIR /app

COPY config.json /app/config.json
COPY rag_agent.py /app/rag_agent.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "rag_agent.py"]
