# Use an official Python image
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["streamlit", "run", "agents/main.py", "--server.port=80", "--server.address=0.0.0.0"]