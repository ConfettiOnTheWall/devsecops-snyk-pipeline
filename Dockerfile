# Intentionally pinned to an older base image so `snyk container test`
# has real OS-level vulnerabilities to report, not just Python deps.
FROM python:3.9-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["python", "main.py"]
