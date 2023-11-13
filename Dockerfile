FROM python:3.9
WORKDIR /Verba
COPY . /Verba
RUN pip install -e '.'
EXPOSE 8000
CMD ["verba", "start"]