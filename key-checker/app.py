from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(name)

# Параметры подключения к базе данных
DATABASE_URL = "postgresql://ludiflex_admin:joker1337@34.30.158.137:5432/ludiflex"
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

@app.route('/api/activate', methods=['POST'])
def activate_key():
    key = request.json.get('key')  # Получаем ключ из запроса
    if not key:
        return jsonify({"valid": False, "message": "Ключ не предоставлен"})

    try:
        # Проверяем ключ в базе данных и проверяем его срок действия
        query = """
        SELECT * FROM activation_key 
        WHERE key = %s 
        AND used = FALSE 
        AND expires_at > %s
        """
        cursor.execute(query, (key, datetime.utcnow()))  # Сравниваем с текущей датой
        result = cursor.fetchone()

        if result:
            # Ключ действителен
            return jsonify({"valid": True, "message": "Ключ действителен"})
        else:
            return jsonify({"valid": False, "message": "Неверный или просроченный ключ"})
    
    except Exception as e:
        return jsonify({"valid": False, "message": str(e)})

if name == 'main':
    app.run(host='0.0.0.0', port=5050)
