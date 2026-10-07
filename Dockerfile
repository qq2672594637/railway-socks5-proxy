FROM python:3.13-alpine

COPY http_proxy.py /opt/http_proxy.py
COPY entrypoint.sh /usr/local/bin/proxy-entrypoint
RUN chmod 0755 /usr/local/bin/proxy-entrypoint

ENV PROXY_PORT=1080

EXPOSE 1080
ENTRYPOINT ["/usr/local/bin/proxy-entrypoint"]