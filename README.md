## Контейнеризованный асинхронный (фреймворк aiohttp) REST API (backend) для сайта объявлений.
#### Реализованы методы создания нового пользователя/получения токена зарегистрированным пользователем, создания/удаления/редактирования/получения всех объявлений или одного  объявления.
#### Создавать объявление может только авторизованный пользователь. Удалять/редактировать может только владелец объявления. 

### для запуска приложения в корне проекта:
* создать файл `.env`. В нем указать переменные:
    * POSTGRES_USER=username
    * POSTGRES_PASSWORD=password
    * POSTGRES_DB=db_name
* в командной строке ввести команду: `docker-compose up`


#### Примеры запросов в файле ```requests.http```