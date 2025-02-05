FROM python:3.11-slim

RUN python -m pip install -U pip
RUN python -m pip install pipx
RUN pipx install poetry==1.8.4
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /src
COPY poetry.lock pyproject.toml Makefile ./
COPY ./src ./

RUN poetry install
RUN poetry run python manage.py collectstatic --noinput
RUN poetry run python manage.py migrate

EXPOSE 8000

ENV PYTHONPATH=src
ENTRYPOINT ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]