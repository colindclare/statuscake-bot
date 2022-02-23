FROM python:3.6.8-alpine

# First setup any dependencies at the OS level that python will want...
RUN apk add --no-cache gcc libc-dev libffi-dev mysql mysql-dev mysql-client
RUN pip install --upgrade pip
RUN pip install pipenv

# Now we Install dependencies
RUN pipenv install

# Finally we set the entry point...
# For now it's commented out to have no entry point and just start a container....
# CMD ["/usr/local/bin/python", "kudo.py"]
ENTRYPOINT [ "run-scbot.sh" ]