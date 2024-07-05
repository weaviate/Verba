FROM python:3.11
WORKDIR /Verba
COPY . /Verba
RUN pip install -e '.'
EXPOSE 8000
CMD ["verba", "start","--port","8000","--host","0.0.0.0"]
# Set permissions so that docker containers can see the mapped container folder correctly:
RUN chmod 755 /app && \
    chmod 644 /app/* && \
    chown -R nobody:nogroup /app

USER nobody
