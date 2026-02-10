FROM python:3.9-slim
WORKDIR /app
COPY dashboard/backend/requirements.txt /app/dashboard/backend/requirements.txt
RUN pip install -r /app/dashboard/backend/requirements.txt
COPY . /app
EXPOSE 5000
CMD ["python", "/app/dashboard/backend/app.py"]
