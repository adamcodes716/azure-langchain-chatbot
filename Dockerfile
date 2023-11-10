FROM python:3.11-slim

ADD .env .

WORKDIR /app

COPY ./ /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "main.py", "--server.port=80", "--server.address=0.0.0.0"]