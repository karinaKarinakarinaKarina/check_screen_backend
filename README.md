Фронтэнд для данного проекта: https://github.com/LizaEmelyanova/screen-check </br>
Для корректной работы приложения необходимо запустить сервер Next.js и сервер Django. </br>
Запуск сервера: python manage.py runserver </br>
http://localhost:8000 - главная страница с основным функционалом </br>
http://localhost:8000/api/yolo-model-info/ - вывод классов модели для проверки корректной загрузки модели </br>
</br>
</br> 
Для сборки контейнера: docker build -t checkscreen_app . </br>
Для запуска контейнера: docker run -p 8000:8000 -p 3000:3000 checkscreen_app </br>
