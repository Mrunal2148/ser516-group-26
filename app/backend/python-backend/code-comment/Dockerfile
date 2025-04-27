FROM python:3.13-slim

WORKDIR /app
RUN apt-get update && apt-get install -y git

COPY python-backend/code-comment/requirements.txt .
COPY python-backend/code-comment/code_comment_app.py .
COPY utilities ./utilities

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5006

CMD ["python", "code_comment_app.py"]
