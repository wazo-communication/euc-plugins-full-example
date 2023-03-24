# Wazo Example Plugin

to build

    docker build -t euc-example .

To run

    docker run -d -e WAZO_HOST=<wazo host> -e WAZO_USERNAME=<wazo username> -e WAZO_PASSWORD=<wazo password> -p 8088:8888 -t euc-example

To use it on WDA modify the key manifest_urls add add the good value http://MY_URL/content/manifest.json
