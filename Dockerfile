# See docker/base
FROM phusion_0.10.0_updated-apt:2018-02-19

RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip

RUN apt-get install -y git

RUN apt-get install -y nginx

# --- System-level app dependencies (& python dependencies' system dependencies)
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

# --- Copy pip package tarballs into image
RUN mkdir /tonetutor
COPY docker /tonetutor/docker/

# --- Python app dependencies
#RUN pip3 install -r /tonetutor/tonetutor/requirements_docker.txt
RUN pip3 install django==1.10
RUN pip3 install mutagen
RUN pip3 install pytaglib==1.4.1
RUN pip3 install django-user_agents==0.3.0
RUN pip3 install psycopg2-binary
RUN pip3 install gunicorn
RUN pip3 install django-registration==2.1.2
RUN pip3 install stripe
RUN pip3 install django-sitetree
RUN pip3 install pytest
RUN pip3 install django-pytest
RUN pip3 install djangorestframework

RUN pip3 install git+git://github.com/jivanamara/ttlib@v0.2.3#egg=ttlib==0.2.3
#RUN pip3 install /tonetutor/docker/dependencies/ttlib-0.2.3.tar.gz
RUN pip3 install git+git://github.com/jivanamara/syllable-samples@v0.2.1#egg=syllable-samples==0.2.1
#RUN pip3 install /tonetutor/docker/dependencies/syllable-samples-0.2.1.tar.gz
RUN pip3 install git+git://github.com/jivanamara/hanzi-basics@v1.1.2#egg=hanzi-basics==1.1.2
#RUN pip3 install /tonetutor/docker/dependencies/hanzi-basics-1.1.2.tar.gz
RUN pip3 install git+git://github.com/jivanamara/tonerecorder@v1.1.6#egg=tonerecorder==1.1.6
#RUN pip3 install /tonetutor/docker/dependencies/tonerecorder-1.1.6.tar.gz
RUN pip3 install git+git://github.com/jivanamara/tonetutor-webapi@v0.3.6#egg=tonetutor-webapi==0.3.6
#RUN pip3 install /tonetutor/docker/dependencies/tonetutor_webapi-0.0.1.tar.gz
RUN pip3 install git+git://github.com/jivanamara/tonetutor-usermgmt@v0.4.2#egg=tonetutor-usermgmt==0.4.1

# Copy code & configuration into image
COPY tonetutor /tonetutor/tonetutor/
COPY webui /tonetutor/webui/
COPY manage.py /tonetutor/

# Set up nginx
RUN rm /etc/nginx/sites-enabled/default
RUN cp /tonetutor/docker/nginx/tonetutor.nginx /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/tonetutor.nginx /etc/nginx/sites-enabled

# Set up tkSnack (python audio package)
WORKDIR /tonetutor/docker/dependencies/snack_2.2.10/python/
RUN python3 setup.py install
WORKDIR /

# --- Django setup
RUN mkdir /tonetutor-static
# Set expected environment variables.  They're needed to run, but won't be used for this command.
RUN SECRET_KEY='tempsecretkey' EMAIL_USER='nouser' EMAIL_PASS='nopass' python3 /tonetutor/manage.py collectstatic --noinput

# --- Cron job scripts & scheduling
COPY docker/cron/ /etc/cron.d/
RUN /bin/bash -c 'chmod 444 /etc/cron.d/*'
COPY docker/scripts/ /scripts/
RUN /bin/bash -c 'chmod 544 /scripts/*'
# Needed for sync_audio_with_s3 script
RUN apt-get install -y awscli

# --- Scripts to run at container start
# Unfortunately this is preventing startup.  Migrations will have to be done manually.
#COPY docker/my_init.d/migrate_django_db.sh /etc/my_init.d/

# --- Services to start at container start
COPY docker/service /etc/service

# Run With:
# docker run --name <container-name> -e SECRET_KEY=<site-secret-key> -e DB_PASS=<db-pass> -e STRIPE_SECRET_KEY=<stripe-secret-key> -e STRIPE_PUBLISHABLE_KEY=<stripe-publishable-key> -e EMAIL_HOST=<email-host> -e EMAIL_USER=<registration-sender> -e EMAIL_PASS=<email-pass> -e AWS_ACCESS_KEY_ID=<key-id> -e AWS_SECRET_ACCESS_KEY=<key> -e AWS_DEFAULT_REGION=<region> -dit -p <host_port>:80 -v /mnt/data-volume/tonetutor-media/:/mnt/data-volume/tonetutor-media/ --add-host=database-host:<host-ip> <image>
# Enter the container and run migrations 'xvfb-run -a python3 /tonetutor/manage.py migrate --noinput'
