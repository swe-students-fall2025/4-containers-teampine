FROM python:3.10

# Note: Using full python image (not slim) for complete SSL/TLS support needed by MongoDB Atlas

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
CMD ["python", "app/app.py"]
