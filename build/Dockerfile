# syntax=docker/dockerfile:1

FROM python:3.11-alpine

COPY requirements.txt rpilocator-rss-ntfy.py /
RUN <<EOT
    set -eux
    pip3 install -r requirements.txt
EOT

CMD ["python3", "-u", "rpilocator-rss-ntfy.py"]
