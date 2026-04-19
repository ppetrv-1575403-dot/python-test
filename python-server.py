#!/usr/bin/env python3
"""
Простой HTTP сервер с лучшими практиками:
- Логирование запросов
- Безопасные заголовки
- Поддержка разных MIME типов
- Graceful shutdown
"""

import http.server
import socketserver
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Кастомный обработчик с улучшениями безопасности"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path.cwd() / 'public'), **kwargs)
    
    def end_headers(self):
        """Добавляем безопасные заголовки"""
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Переопределяем логирование"""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/api/health':
            self.send_json_response({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
            return
        elif self.path == '/api/info':
            self.send_json_response({
                'server': 'Python Simple HTTP Server',
                'version': '1.0.0',
                'paths': ['/', '/api/health', '/api/info']
            })
            return
        
        # Обслуживание статических файлов
        logger.info("Обслуживание статических файлов")
        super().do_GET()
    
    def send_json_response(self, data):
        """Отправка JSON ответа"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def handle_error(self):
        """Обработка ошибок"""
        logger.error(f"Error handling request: {self.path}")
        self.send_response(500)
        self.end_headers()

def create_public_directory():
    """Создание директории для статических файлов"""
    public_dir = Path('public')
    public_dir.mkdir(exist_ok=True)
    
    # Создаем index.html по умолчанию
    index_file = public_dir / 'index.html'
    if not index_file.exists():
        index_file.write_text("""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>!!!Python Web Server by Pavel Petrov ?</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #333; }
        .status { color: #4CAF50; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🚀 Python Web Server by Pavel Petrov _</h1>
    <p>Сервер успешно запущен!</p>
    <p class="status">● Работает</p>
    <p>Доступные API: <code>/api/health</code>, <code>/api/info</code></p>
</body>
</html>
        """, encoding='utf-8')
        logger.info("Created default index.html")

def run_server(port=8000):
    """Запуск сервера"""
    try:
        # Создаем директорию для статики
        create_public_directory()
        
        # Создаем сервер с обработчиком
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            logger.info(f"Сервер запущен на http://localhost:{port}")
            logger.info(f"Статические файлы из директории: ./public/")
            logger.info("Нажмите Ctrl+C для остановки")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                logger.info("\nОстановка сервера...")
                httpd.shutdown()
                
    except OSError as e:
        logger.error(f"Ошибка при запуске сервера: {e}")
        if e.errno == 98 or e.errno == 10048:
            logger.info(f"Порт {port} занят. Попробуйте другой порт")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)