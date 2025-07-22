from flask import Flask, request, jsonify
import os
import psycopg2
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Конфигурация базы данных
DB_CONFIG = {
    'host': '34.30.158.137',
    'database': 'ludiflex',
    'user': 'ludiflex_admin',
    'password': 'joker1337'
}

# Путь для загрузки файлов
UPLOAD_FOLDER = '/home/desollatecore/settings-for-server/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

@app.route('/get_files', methods=['GET'])
def get_files():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id parameter is required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем активные ключи пользователя
        cur.execute("""
            SELECT a.key, p.folder_path 
            FROM activation_key a
            JOIN package p ON a.package_id = p.id
            WHERE a.user_id = %s AND a.used = TRUE 
            AND (a.expires_at IS NULL OR a.expires_at > NOW())
        """, (user_id,))
        
        active_keys = cur.fetchall()
        
        if not active_keys:
            return jsonify({'error': 'No active subscriptions found'}), 403
        
        # Собираем все файлы из доступных папок
        files = []
        for key, folder_path in active_keys:
            full_path = os.path.join(UPLOAD_FOLDER, folder_path)
            if os.path.exists(full_path):
                for filename in os.listdir(full_path):
                    file_path = os.path.join(full_path, filename)
                    if os.path.isfile(file_path):
                        files.append({
                            'name': filename,
                            'url': f'http://34.30.158.137/download?file={filename}&key={key}',
                            'preview': f'http://34.30.158.137/preview?file={filename}&key={key}' if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else None
                        })
        
        return jsonify({'children': files})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('file')
    key = request.args.get('key')
    
    if not filename or not key:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем валидность ключа
        cur.execute("""
            SELECT p.folder_path 
            FROM activation_key a
            JOIN package p ON a.package_id = p.id
            WHERE a.key = %s AND a.used = TRUE 
            AND (a.expires_at IS NULL OR a.expires_at > NOW())
        """, (key,))
        
        result = cur.fetchone()
        
        if not result:
            return jsonify({'error': 'Invalid or expired key'}), 403
        
        folder_path = result[0]
        full_path = os.path.join(UPLOAD_FOLDER, folder_path, secure_filename(filename))
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(full_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/preview', methods=['GET'])
def preview_file():
    filename = request.args.get('file')
    key = request.args.get('key')
    
    if not filename or not key:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем валидность ключа
        cur.execute("""
            SELECT p.folder_path 
            FROM activation_key a
            JOIN package p ON a.package_id = p.id
            WHERE a.key = %s AND a.used = TRUE 
            AND (a.expires_at IS NULL OR a.expires_at > NOW())
        """, (key,))
        
        result = cur.fetchone()
        
        if not result:
            return jsonify({'error': 'Invalid or expired key'}), 403
        
        folder_path = result[0]
        full_path = os.path.join(UPLOAD_FOLDER, folder_path, secure_filename(filename))
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(full_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/check_subscription', methods=['GET'])
def check_subscription():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id parameter is required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем активные подписки пользователя
        cur.execute("""
            SELECT a.key, p.name, a.expires_at
            FROM activation_key a
            JOIN package p ON a.package_id = p.id
            WHERE a.user_id = %s AND a.used = TRUE 
            AND (a.expires_at IS NULL OR a.expires_at > NOW())
        """, (user_id,))
        
        active_keys = cur.fetchall()
        
        if not active_keys:
            return jsonify({'status': 'inactive'})
        
        # Возвращаем первый активный ключ (можно адаптировать для нескольких ключей)
        key, package_name, expires_at = active_keys[0]
        return jsonify({
            'status': 'active',
            'key': key,
            'package': package_name,
            'expires_at': expires_at.isoformat() if expires_at else None
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/activate_key', methods=['POST'])
def activate_key():
    key = request.form.get('key')
    user_id = request.form.get('user_id')
    
    if not key or not user_id:
        return jsonify({'error': 'key and user_id parameters are required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем ключ в базе
        cur.execute("""
            SELECT id, used, expires_at 
            FROM activation_key 
            WHERE key = %s AND (user_id IS NULL OR user_id = %s)
        """, (key, user_id))
        
        key_data = cur.fetchone()
        
        if not key_data:
            return jsonify({'error': 'Key not found'}), 404
        
        key_id, used, expires_at = key_data
        
        if used:
            return jsonify({'error': 'Key already used'}), 403
        
        if expires_at and expires_at < datetime.now():
            return jsonify({'error': 'Key expired'}), 403
        
        # Активируем ключ
        cur.execute("""
            UPDATE activation_key 
            SET used = TRUE, user_id = %s 
            WHERE id = %s
        """, (user_id, key_id))
        
        conn.commit()
        
        return jsonify({'status': 'success', 'message': 'Key activated successfully'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
