# Wazo Example Plugin

to build

    docker build -t euc-example .

To run

    docker run -d -e WAZO_HOST=<wazo host> -e WAZO_USERNAME=<wazo username> -e WAZO_PASSWORD=<wazo password> -p 8088:8888 -t euc-example

To use it on WDA

Modify the key manifest_urls and add it the good value

    http://<URL>/content/manifest.json
