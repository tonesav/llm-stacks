FROM python:3.11

WORKDIR /app

COPY config.json /app/config.json
COPY crew_agent.py /app/crew_agent.py
COPY supervisor.py /app/supervisor.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "crew_agent.py"]
