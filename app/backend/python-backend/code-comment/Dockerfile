FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY code-comment-app.py .

EXPOSE 5006

CMD ["python", "code-comment-app.py"]
