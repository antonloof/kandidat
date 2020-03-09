#! /bin/bash
cp kandidat_nginx.conf /etc/nginx/sites-enabled/kandidat_nginx.conf
source backend/venv/bin/activate
sh -c 'cd backend/measure && ./manage.py collectstatic --no-input'
uwsgi --ini backend/measure.ini &
#sh -c 'cd frontend/measure && npm run-script ng build -- --prod'

mkdir -p /var/www/html/measure
cp -r frontend/measure/dist/measure/* /var/www/html/measure

/etc/init.d/nginx restart

