FROM python:3.9

COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# install crontab
# RUN apt-get update
# RUN apt-get install -y cron
# RUN service cron start

# RUN python manage.py crontab add 
# RUN service cron start 

# running migrations
# RUN python manage.py migrate
RUN python manage.py collectstatic --clear --noinput

# ENTRYPOINT ["./docker-entrypoint.sh"] 

# gunicorn
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]

