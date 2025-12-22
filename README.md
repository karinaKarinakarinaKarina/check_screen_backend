Фронтэнд для данного проекта: https://github.com/LizaEmelyanova/screen-check </br>
</br>
Для корректной работы приложения необходимо запустить сервер Next.js и сервер Django. </br>
Запуск сервера: python manage.py runserver </br>
http://localhost:8000 - главная страница с основным функционалом </br>
http://localhost:8000/api/yolo-model-info/ - вывод классов модели для проверки корректной загрузки модели </br>
</br>
</br> 
Для сборки контейнера: docker build -t checkscreen_app . </br>
Для запуска контейнера: docker run -p 8000:8000 -p 3000:3000 checkscreen_app </br>

</br>
</br> 
Check Screen - приложение, позволяющее определять сайты (скриншоты или фотография монитора). </br>
В качестве frontend использовался Next.js, backend реализован на python c помощью фрейморка Django. </br>
В качестве модели использовалась YOLO8s, которую мы обучали самостоятельно на собранном датасете. Датасет был составлен командой и размечен на Roboflow для дальнейшего обучения. </br>
Были определены следующие классы:  aliexpress, google, ozon, pinterest, steam, telegram, vk, whatsapp, wildberries, yandex, yandexmusic, youtube </br>
</br>
<img width="1837" height="933" alt="image" src="https://github.com/user-attachments/assets/37c61c17-dc0f-4467-9c1a-f0c042aba1a1" /> </br>
<img width="1796" height="938" alt="image" src="https://github.com/user-attachments/assets/44b7d2d4-6940-4305-8bd0-34573f80f186" /> </br>
<img width="1416" height="827" alt="image" src="https://github.com/user-attachments/assets/e86f08a2-dc84-47e2-95e4-93ac0b56a518" /> </br>
<img width="1422" height="354" alt="image" src="https://github.com/user-attachments/assets/463f0f45-b876-4d06-963a-ded5c89a9249" /> </br>
<img width="1383" height="371" alt="image" src="https://github.com/user-attachments/assets/19ddd316-0ebe-4e9a-a290-9cbd7c0795d0" /> </br>

Работа программы: </br>
<img width="1869" height="954" alt="image" src="https://github.com/user-attachments/assets/8601d31d-0c3e-492a-999d-a5323dd28869" /> </br>
<img width="1839" height="919" alt="image" src="https://github.com/user-attachments/assets/66863617-d013-4414-8e62-69eb0895bf53" /> </br>
Также информация о результатах обработки выводится в консоль: </br>
<img width="971" height="376" alt="image" src="https://github.com/user-attachments/assets/fb64ea93-9e5a-46e1-b8a5-cad98c2ac644" /> </br>

