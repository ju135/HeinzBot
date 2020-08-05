FROM python:latest

WORKDIR /var/www/htdocs

COPY requirements.txt /var/www/htdocs
RUN pip install -r requirements.txt

COPY . /var/www/htdocs

CMD "chown -R 1000:1000 /var/www/htdocs"

CMD python heinz_bot.py