FROM python:3.9 as deps

FROM deps
WORKDIR /Verba
COPY . /Verba
RUN pip install -e '.[dev,huggingface]'
EXPOSE 8000

CMD ["verba", "start"]