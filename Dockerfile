FROM python:3.7.7-slim

RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
    sed -i \
        -e 's/deb.debian.org/mirrors.aliyun.com/g' \
        -e 's/security.debian.org/mirrors.aliyun.com/g' \
        /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    cron && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    pip install --no-cache-dir tornado


COPY image-files /
RUN touch /var/log/cron.log \
 && touch /tmp/ip-txt \
 && mkdir -p /var/work

COPY src /var/work/

# Apply cron job
RUN crontab /var/spool/cron/crontabs/test
EXPOSE 8888
CMD ["python", "/var/work/app.py"]