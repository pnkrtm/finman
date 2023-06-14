FROM python:3.10.11

WORKDIR /opt/finman

COPY src/ /opt/finman/src/

COPY ./requirements.txt /opt/finman/requirements.txt
ENV PYTHONPATH /opt/finman
RUN pip install --no-cache-dir --upgrade -r /opt/finman/requirements.txt
CMD ["python", "/opt/finman/src/finman/main.py", ]