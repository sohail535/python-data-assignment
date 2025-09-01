FROM python:3.12-slim

WORKDIR /app

COPY services/mock_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/mock_api /app

EXPOSE 5050

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5050"]
