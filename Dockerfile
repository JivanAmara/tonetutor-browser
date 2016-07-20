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
RUN pip3 install /tonetutor/docker/dependencies/ttlib-0.1.1.tar.gz
RUN pip3 install mutagen
RUN pip3 install pytaglib
RUN pip3 install gunicorn

WORKDIR /tonetutor/docker/dependencies/snack_2.2.10/python/
RUN python3 setup.py install
WORKDIR /

# --- Django setup
RUN mkdir /tonetutor-static
RUN python3 /tonetutor/manage.py collectstatic --noinput
COPY db.sqlite3 /
ENV PYTHONPATH=/tonetutor/docker/dependencies/snack_2.2.10/python/
RUN xvfb-run python3 /tonetutor/manage.py migrate --noinput

# --- Services to start at container start
COPY docker/service /etc/service

# Run With:
# docker run -dit -p <host_port>:80 <image>
