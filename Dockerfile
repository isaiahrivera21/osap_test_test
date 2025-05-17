FROM python:3.11-slim 

WORKDIR /my_model

ENV LISTEN_PORT=80 

RUN apt update && apt install -y libgomp1
RUN pip3 install poetry 

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false 
RUN poetry install --only main --no-interaction --no-ansi --no-root -vv \
    && rm -rf /root/.cache/pypoetry


COPY . . 
WORKDIR /my_model/src 
ENTRYPOINT [ "unvircoen my_model.serving.__main__:app --host 0.0.0.0 --port ${LISTEN_PORT} --workers 2" ]
