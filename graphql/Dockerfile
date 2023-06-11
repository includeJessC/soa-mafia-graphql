FROM python

WORKDIR /app
COPY ../.. .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m pip install python-multipart
RUN python -m pip install 'uvicorn[standard]'


ENTRYPOINT [ "python", "server_graphql.py" ]