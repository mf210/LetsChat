FROM python:3.10
WORKDIR /letschat
ENV PYTHONDONTWIRTEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY Pipfile Pipfile.lock /letschat/
RUN pip install pipenv && pipenv install --dev --system
