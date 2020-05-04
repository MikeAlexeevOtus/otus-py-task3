# scoring api

Апи с декларативной валидацией запросов

## запуск
апи работает на python 2.7

`python api.py`

По-дефолту сервер слушает на 127.0.0.1:8080

Чтобы проверить работу апи, можно отправлять запросы с тестовыми семплами, например
`curl http://127.0.0.1:8080/method/ -X POST --data @request_samples/score.json`
`curl http://127.0.0.1:8080/method/ -X POST --data @request_samples/interests.json`

## тесты
запуск тестов:
`python test.py`
