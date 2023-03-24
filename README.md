# Wazo Example Plugin

to build
    docker build -t euc-example .

To run
    docker run -e WAZO_HOST=<wazo host> -e WAZO_USERNAME=<wazo username> -e WAZO_PASSWORD=<wazo password> -p 8088:8888 -t euc-example
