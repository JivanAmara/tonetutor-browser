#/bin/bash
PYTHONPATH=/tonetutor/docker/dependencies/snack_2.2.10/python/
xvfb-run -a python3 /tonetutor/manage.py migrate --noinput
exit 0
