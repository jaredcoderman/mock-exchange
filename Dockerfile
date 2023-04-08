FROM python:3.10
WORKDIR /app
COPY ./cour.ttf ./
RUN mkdir -p /usr/share/fonts/truetype/
RUN install -m644 cour.ttf /usr/share/fonts/truetype/
RUN rm ./cour.ttf
RUN pip install poetry
WORKDIR /code
COPY poetry.lock pyproject.toml /code/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
COPY . /code
CMD python main.py