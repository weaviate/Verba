FROM python:3.9 as deps
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

FROM deps
WORKDIR /Verba
COPY . /Verba
RUN pip install -e .
EXPOSE 8000

CMD ["verba", "start"]