FROM python:3.6.8-alpine as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base AS python-deps

# First setup any dependencies at the OS level that python will want...
RUN apk add --no-cache gcc libc-dev libffi-dev mysql mysql-dev mysql-client bash mariadb-connector-c-dev
RUN pip install --upgrade pip
RUN pip install pipenv

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN adduser -S statuscake-bot
WORKDIR /home/statuscake-bot
USER statuscake-bot

# Install application into container
COPY . .
RUN source /.venv/bin/activate

# Finally we set the entry point...
# For now it's commented out to have no entry point and just start a container....
# CMD ["/usr/local/bin/python", "kudo.py"]
ENTRYPOINT ["sh", "/home/statuscake-bot/run-scbot.sh" ]
