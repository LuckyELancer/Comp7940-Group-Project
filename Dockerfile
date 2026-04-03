FROM python:3.12-slim

WORKDIR /Comp7940-Group-Project
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY config.ini .
COPY *.py .
CMD ["python", "chatbot.py"]