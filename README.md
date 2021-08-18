后端启动: uwsgi -i --http 0.0.0.0:8001 --chdir /app/www/project/backend --mount /=./app.py --callable app --daemonize /tmp/backend.log --enable-threads
mysql: alter user 'root'@'localhost' identified by '123456'
编译  npm run build  消耗CPU严重

