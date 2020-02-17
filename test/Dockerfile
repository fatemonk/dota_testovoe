FROM python:3.8

RUN pip install pipenv
WORKDIR /app
COPY Pipfile* /app/
RUN pipenv sync -v --clear
COPY . /app

CMD pipenv run python test.py
