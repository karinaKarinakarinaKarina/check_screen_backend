import re
from django.shortcuts import render

# Create your views here.

import requests
from django.http import HttpResponse
from django.conf import settings
from urllib.parse import urljoin

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