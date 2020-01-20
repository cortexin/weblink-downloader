FROM python:3.8-slim

# ADD Pipfile /apps/link_downloader/Pipfile
# ADD Pipfile.lock /apps/link_downloader/Pipfile.lock

RUN apt-get update && apt install -y python3-pip && pip install pipenv

WORKDIR /apps/link_downloader

ADD . /apps/link_downloader

RUN cd /apps/link_downloader && pipenv  install --system --deploy --ignore-pipfile

CMD uvicorn link_downloader.main:app --host 0.0.0.0