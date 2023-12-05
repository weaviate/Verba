FROM python:3.10
WORKDIR /Verba
COPY . /Verba
RUN pip install -e '.[huggingface]'
EXPOSE 8000
CMD ["verba", "start"]
