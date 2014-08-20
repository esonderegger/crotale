sudo apt-get install git nginx-full uwsgi uwsgi-plugin-python postgresql python-pip python-sqlalchemy python-psycopg2
sudo pip install flask watchdog pexpect

wget http://ffmpeg.gusari.org/static/64bit/ffmpeg.static.64bit.latest.tar.gz
tar -zxvf ffmpeg.static.64bit.latest.tar.gz
sudo cp /home/crotale/ffmpeg /usr/local/bin

sudo -u postgres psql -c "alter user postgres password 'crotalepass';"
sudo -u postgres psql -c "create user crotale createdb createuser password 'crotale';"
sudo -u postgres psql -c "create database crotale owner crotale;"

python crotaleApp/installCrotaleDB.py

sudo mkdir -p /srv/www/crotale/application
sudo mkdir -p /srv/www/crotale/logs
sudo chown www-data:www-data /srv/www/crotale/logs
sudo mkdir -p /srv/www/crotale/uploads
sudo chown www-data:www-data /srv/www/crotale/uploads
sudo mkdir -p /srv/www/crotale/corrected
sudo chown www-data:www-data /srv/www/crotale/corrected

sudo cp /home/crotale/crotale-nginx.conf /etc/nginx/sites-available/crotale
sudo ln -s /etc/nginx/sites-available/crotale /etc/nginx/sites-enabled/crotale
sudo rm /etc/nginx/sites-enabled/default

sudo cp /home/crotale/crotale-uwsgi.xml /etc/uwsgi/apps-available/crotale.xml
sudo ln -s /etc/uwsgi/apps-available/crotale.xml /etc/uwsgi/apps-enabled/crotale.xml

sudo cp -R /home/crotale/crotaleApp/* /srv/www/crotale/application/
sudo service uwsgi restart
sudo service nginx restart
