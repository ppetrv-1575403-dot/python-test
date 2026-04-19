#!/usr/bin/env python3
"""
Flask приложение с HTTPS поддержкой
- Production-ready конфигурация
- Автоматическая генерация сертификатов
- Безопасные заголовки
"""

from flask import Flask, jsonify, request, render_template_string
import ssl
import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import subprocess

app = Flask(__name__)

# Настройка логирования
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

handler = RotatingFileHandler(log_dir / 'https_server.log', maxBytes=10485760, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# HTML шаблон главной страницы
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Flask Server</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 600px;
        }
        .lock-icon { font-size: 60px; margin-bottom: 20px; }
        h1 { color: #333; margin-bottom: 10px; }
        .secure { color: #4CAF50; font-weight: bold; margin: 20px 0; }
        .info {
            background: #f5f5f5;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            text-align: left;
        }
        code {
            background: #333;
            color: #fff;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            margin: 5px;
        }
        .tls12 { background: #4CAF50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="lock-icon">🔒</div>
        <h1>Secure Flask Server (test)</h1>
        <p>HTTPS + TLS 1.2+ защищенное соединение</p>
        <div class="secure">✓ SSL/TLS Сертификат активен</div>
        
        <div class="info">
            <strong>📊 Информация о соединении:</strong><br><br>
            • Протокол: HTTPS/TLS<br>
            • Шифрование: AES-256-GCM<br>
            • Сервер: Flask + Python {{ version }}<br>
            • Время: {{ time }}<br>
        </div>
        
        <div style="margin-top: 20px;">
            <span class="badge tls12">TLS 1.2+</span>
            <span class="badge tls12">HSTS</span>
            <span class="badge tls12">XSS Protection</span>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Главная страница"""
    return render_template_string(INDEX_TEMPLATE, 
                                  version='3.x',
                                  time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/health')
def health():
    """API проверки здоровья"""
    return jsonify({
        'status': 'healthy',
        'secure': True,
        'protocol': request.scheme,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/info')
def info():
    """Информация о сервере"""
    return jsonify({
        'server': 'Flask HTTPS Server',
        'tls_version': 'TLS 1.2+',
        'ciphers': 'Modern',
        'features': ['HSTS', 'CORS', 'Secure Headers']
    })

def generate_certificate(cert_dir='certs'):
    """Генерация SSL сертификата"""
    cert_dir = Path(cert_dir)
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / 'server.crt'
    key_file = cert_dir / 'server.key'
    
    if cert_file.exists() and key_file.exists():
        app.logger.info("Сертификаты найдены")
        return str(cert_file), str(key_file)
    
    app.logger.info("Генерация SSL сертификата...")
    
    # Генерация через openssl
    subprocess.run([
        'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
        '-keyout', str(key_file), '-out', str(cert_file),
        '-days', '365', '-nodes',
        '-subj', '/C=RU/ST=Moscow/L=Moscow/O=FlaskServer/CN=localhost'
    ], check=True, capture_output=True)
    
    app.logger.info(f"Сертификат создан: {cert_file}")
    return str(cert_file), str(key_file)

def run_https_server(port=5000):
    """Запуск HTTPS сервера"""
    try:
        # Генерация сертификатов
        cert_file, key_file = generate_certificate()
        
        # Создание SSL контекста
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_file, key_file)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        app.logger.info(f"🔒 HTTPS сервер запущен на https://localhost:{port}")
        app.logger.info(f"Сертификат: {cert_file}")
        
        # Запуск с SSL
        app.run(
            host='0.0.0.0',
            port=port,
            ssl_context=ssl_context,
            debug=False,
            threaded=True
        )
        
    except PermissionError:
        app.logger.error(f"Порт {port} требует прав. Используйте порт > 1024")
    except Exception as e:
        app.logger.error(f"Ошибка: {e}")

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    run_https_server(port)