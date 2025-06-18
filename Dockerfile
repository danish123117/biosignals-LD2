FROM python:3.11.13-slim-bookworm


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential  \
        gcc g++ make      \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /myapp
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && python -m pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 3002
CMD ["python", "server.py"]
