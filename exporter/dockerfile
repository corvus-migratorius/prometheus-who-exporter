FROM python:3.9.21-slim

WORKDIR /exporter

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN getent group utmp || groupadd utmp && \
    useradd -M -g utmp user

COPY . .

RUN chown -R user:utmp /exporter

USER user

ENTRYPOINT ["python", "exporter.py"]

