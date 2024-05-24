FROM python:3.11.9-alpine3.19
RUN mkdir /myapp
WORKDIR /myapp
COPY . .
RUN python3 -m pip install -r requirements.txt
EXPOSE 3002 
CMD ["python3", "server.py"]