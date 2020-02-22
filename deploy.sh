#! /bin/bash
cp kandidat_nginx.conf /etc/nginx/sites-enabled/kandidat_nginx.conf
source backend/measure/venv/bin/activate
sh -c 'cd backend/measure && ./manage.py collectstatic --no-input'
uwsgi --ini backend/measure.ini &
sh -c 'cd frontend/measure && ng build --prod'
cp -r frontend/measure/dist/measure/* /var/www/html/measure
/etc/init.d/nginx restart

