tar -zcvf crotale-$(date +"%Y-%m-%d-%H-%M-%S").tar.gz /srv/www/crotale/application
rm -rf /srv/www/crotale/application/*
cp -R /home/crotale/crotaleApp/* /srv/www/crotale/application/
service uwsgi restart
service nginx restart
