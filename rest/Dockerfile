FROM python:3.8

WORKDIR /app
COPY . .
RUN python -m pip install -r requirements.txt
RUN python -m pip install python-multipart
ENTRYPOINT ["python", "server.py" ]