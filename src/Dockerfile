FROM python:3.13-slim

LABEL authors="Shizo15"

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "src/main.py"]
