import re
from django.shortcuts import render

# Create your views here.

import requests
from django.http import HttpResponse
from django.conf import settings
from urllib.parse import urljoin
from ultralytics import YOLO
import base64
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from datetime import datetime
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image




# Загрузка модели (лучше вынести в отдельный модуль или использовать ленивую загрузку)
def get_yolo_model():
    # Возвращает загруженную модель
    # Можно загружать разные модели в зависимости от задачи
    model = YOLO('model/runs/detect/train/weights/best.pt')  
    return model



def nextjs_proxy(request, path=''):
    nextjs_url = getattr(settings, 'NEXTJS_URL', 'http://localhost:3000')
    full_url = urljoin(nextjs_url, path)
    
    query_string = request.META.get('QUERY_STRING', '')
    if query_string:
        full_url += f'?{query_string}'
    
    try:
        response = requests.get(full_url, timeout=5)
        content = response.content.decode('utf-8')
        
        # Исправляем пути к статическим файлам
        if response.headers.get('Content-Type', '').startswith('text/html'):
            # Заменяем относительные пути на абсолютные к Next.js серверу
            content = re.sub(
                r'src="/(_next/|assets/|images/)',
                f'src="{nextjs_url}/\\1',
                content
            )
            content = re.sub(
                r'href="/(_next/|assets/|images/)',
                f'href="{nextjs_url}/\\1',
                content
            )
            content = re.sub(
                r'url\(\s*[\'"]?/(_next/|assets/|images/)',
                f'url(\'{nextjs_url}/\\1',
                content
            )
            
            # Также заменяем в script и link тегах
            content = re.sub(
                r'content="/(_next/|assets/|images/)',
                f'content="{nextjs_url}/\\1',
                content
            )
        
        django_response = HttpResponse(
            content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'text/html')
        )
        
        return django_response
        
    except requests.RequestException as e:
        return HttpResponse(
            f'Next.js server unavailable: {str(e)}',
            status=503,
            content_type='text/plain'
        )
    

@csrf_exempt
def process_image_api(request):
    """API для обработки изображения YOLO"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        # Проверяем наличие файла
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Валидация файла
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        file_ext = os.path.splitext(image_file.name)[1].lower()
        
        if file_ext not in allowed_extensions:
            return JsonResponse({
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }, status=400)
        
        # Ограничение размера файла (например, 10MB)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse({'error': 'File size exceeds 10MB limit'}, status=400)
        
        # Генерация уникального имени файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        safe_filename = f"{timestamp}{file_ext}"
        
        # Сохраняем временно
        temp_dir = 'temp_uploads'
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, safe_filename)
        
        with open(temp_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Обработка изображения YOLO
        results = process_image_with_yolo(temp_path)
        
        # Читаем обработанное изображение
        with open(results['processed_image_path'], 'rb') as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Очистка временных файлов
        os.remove(temp_path)
        os.remove(results['processed_image_path'])
        
        # Подготовка ответа
        response_data = {
            'success': True,
            'filename': image_file.name,
            'detections': results['detections'],
            'detection_count': len(results['detections']),
            # Можно добавить статистику по классам
            'class_summary': results.get('class_summary', {}),
            'processed_image': f"data:image/jpeg;base64,{encoded_image}",
            'processing_time': results.get('processing_time', 0)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        # Логирование ошибки
        print(f"Error processing image: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def process_image_with_yolo(image_path):
    """Обработка изображения с YOLO и сохранение результата"""
    start_time = datetime.now()
    
    # Загрузка модели
    model = get_yolo_model()
    
    # Загрузка изображения
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read image")
    
    # Конвертация из BGR в RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Обработка YOLO
    results = model(img_rgb)
    
    # Подготовка результатов
    detections = []
    class_counter = {}
    
    # Рисование bounding boxes
    for result in results:
        for box in result.boxes:
            # Координаты
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            # Класс и уверенность
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names[class_id]
            
            # Счетчик классов
            class_counter[class_name] = class_counter.get(class_name, 0) + 1
            
            # Сохраняем детекцию
            detections.append({
                'class': class_name,
                'class_id': class_id,
                'confidence': round(confidence, 3),
                'bbox': {
                    'x1': int(x1),
                    'y1': int(y1),
                    'x2': int(x2),
                    'y2': int(y2),
                    'width': int(x2 - x1),
                    'height': int(y2 - y1)
                },
                'center': {
                    'x': int((x1 + x2) / 2),
                    'y': int((y1 + y2) / 2)
                }
            })
            
            # Рисуем bounding box
            color = (0, 255, 0)  # Зеленый
            thickness = 2
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
            
            # Добавляем текст с классом и уверенностью
            label = f"{class_name}: {confidence:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            text_thickness = 1
            
            # Размер текста для фона
            (text_width, text_height), _ = cv2.getTextSize(
                label, font, font_scale, text_thickness
            )
            
            # Прямоугольник под текст
            cv2.rectangle(
                img, 
                (int(x1), int(y1) - text_height - 5),
                (int(x1) + text_width, int(y1)),
                color,
                -1  # Заполненный
            )
            
            # Сам текст
            cv2.putText(
                img, 
                label,
                (int(x1), int(y1) - 5),
                font,
                font_scale,
                (0, 0, 0),  # Черный текст
                text_thickness
            )
    
    # Сохранение обработанного изображения
    output_dir = 'processed_images'
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.basename(image_path)
    output_path = os.path.join(output_dir, f"processed_{base_name}")
    
    # Сохраняем как JPEG
    cv2.imwrite(output_path, img)
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    return {
        'detections': detections,
        'class_summary': class_counter,
        'processed_image_path': output_path,
        'processing_time': processing_time
    }

@csrf_exempt
def yolo_model_info(request):
    """Информация о доступных классах модели"""
    if request.method == 'GET':
        try:
            model = get_yolo_model()
            classes = {i: name for i, name in model.names.items()}
            
            return JsonResponse({
                'success': True,
                'model_name': 'YOLOv8',
                'classes': classes,
                'class_count': len(classes)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)