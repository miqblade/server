import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Абсолютный путь до папки с файлами/пресетами
BASE_DIR = os.path.abspath('/home/desollatecore/settings-for-server/uploads')

# Укажи реальный IP и порт, на котором будет работать сервер
SERVER_IP = '34.30.158.137'  # ← замени на свой IP
SERVER_PORT = 5050          # ← замени, если 5000 занят

@app.route('/api/list', methods=['GET'])
def list_files():
    result = []

    for root, dirs, files in os.walk(BASE_DIR):
        rel_root = os.path.relpath(root, BASE_DIR).replace("\\", "/")
        for f in files:
            path = os.path.join(rel_root, f).replace("\\", "/")
            result.append({
                "name": f,
                "path": path,
                "url": f"http://{SERVER_IP}:{SERVER_PORT}/files/{path}"
            })

    return jsonify(result)

@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_from_directory(BASE_DIR, filename)

# Запуск сервера на 5050 порту
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)
