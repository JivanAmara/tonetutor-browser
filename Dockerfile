FROM phusion/baseimage

RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip

RUN apt-get install -y git

RUN apt-get install -y nginx

# --- System-level app dependencies (& python dependencies system dependencies)
RUN apt-get install -y python3-numpy
RUN apt-get install -y python3-scipy
RUN apt-get install -y python3-tk
RUN apt-get install -y python-dev
RUN apt-get install -y libtaglib-ocaml-dev
RUN apt-get install -y xvfb
RUN apt-get install -y libsnack2
RUN apt-get install -y libav-tools
RUN apt-get install -y normalize-audio
RUN apt-get install -y libpq-dev

RUN mkdir /tonetutor
COPY docker /tonetutor/docker/
COPY tonetutor /tonetutor/tonetutor/
COPY webui /tonetutor/webui/
COPY manage.py /tonetutor/

RUN rm /etc/nginx/sites-enabled/default
RUN cp /tonetutor/docker/nginx/tonetutor.nginx /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/tonetutor.nginx /etc/nginx/sites-enabled

# --- Python app dependencies
#RUN pip3 install -r /tonetutor/tonetutor/requirements_docker.txt
RUN pip3 install django
RUN pip3 install mutagen
RUN pip3 install pytaglib
RUN pip3 install django-user_agents==0.3.0
RUN pip3 install /tonetutor/docker/dependencies/ttlib-0.2.2.tar.gz
RUN pip3 install /tonetutor/docker/dependencies/syllable-samples-0.1.4.tar.gz
RUN pip3 install /tonetutor/docker/dependencies/hanzi-basics-1.1.2.tar.gz
RUN pip3 install /tonetutor/docker/dependencies/tonerecorder-1.1.1.tar.gz
RUN pip3 install psycopg2
RUN pip3 install gunicorn
RUN pip3 install django-registration==2.1.2

WORKDIR /tonetutor/docker/dependencies/snack_2.2.10/python/
RUN python3 setup.py install
WORKDIR /

# --- Django setup
RUN mkdir /tonetutor-static
# Set expected environment variables.  They're needed to run, but won't be used for this command.
RUN SECRET_KEY='tempsecretkey' EMAIL_USER='nouser' EMAIL_PASS='nopass' python3 /tonetutor/manage.py collectstatic --noinput

# --- Scripts to run at container start
# Unfortunately this is preventing startup.  Migrations will have to be done manually.
#COPY docker/my_init.d/migrate_django_db.sh /etc/my_init.d/

# --- Services to start at container start
COPY docker/service /etc/service

# Run With:
# docker run -e SECRET_KEY=<secret-key> -e EMAIL_USER=<email-user> -e EMAIL_PASS=<email-pass> -dit -p <host_port>:80 -v /mnt/data-volume/tonetutor-media/:/mnt/data-volume/tonetutor-media/ --add-host=database-host:<host-ip> <image>
# Enter the container and run migrations 'xvfb-run -a python3 /tonetutor/manage.py migrate --noinput'
