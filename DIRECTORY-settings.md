# marIDE  
**mar-ide/PLUGIN-FOR-LZT**

---

## 📂 Создание FILEBROWSER для управления файлами на сервере (Linux)

### 🔧 Установка

```bash
sudo apt update && sudo apt install curl -y
curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash
sudo mkdir -p /srv/files
filebrowser -r /srv/files -p 8080 --address 0.0.0.0
```

---

### 🌐 Узнать внешний IP сервера

```bash
curl ifconfig.me
```

---

### 🚀 Ручной запуск админ-панели

```bash
filebrowser -r /srv/files -p 8080 --address 0.0.0.0
```

---

## ⚙️ Автозапуск FileBrowser через systemd

### 🔍 Узнать путь к бинарнику

```bash
which filebrowser
```

Обычно это `/usr/local/bin/filebrowser`

---

### 📁 Подготовка папок

```bash
sudo mkdir -p /srv/filebrowser
sudo chown -R <ВАШ_ЮЗЕР> /srv/filebrowser
```

Замените `<ВАШ_ЮЗЕР>` на свой логин, например `desollatecore`.

---

### 📝 Создание systemd сервиса

```bash
sudo nano /etc/systemd/system/filebrowser.service
```

Вставьте:

```
[Unit]
Description=FileBrowser Admin Panel
After=network.target

[Service]
User=<ВАШ_ЮЗЕР>
WorkingDirectory=/srv/filebrowser
ExecStart=/usr/local/bin/filebrowser -r /srv/files -p 8080 --address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

---

### ✅ Активация сервиса

```bash
sudo systemctl daemon-reload
sudo systemctl enable filebrowser
sudo systemctl start filebrowser
```

Проверка:

```bash
sudo systemctl status filebrowser
```

---

## 🔐 Как узнать логин и пароль от FileBrowser

```bash
journalctl -u filebrowser.service --no-pager | grep "User 'admin' initialized"
```

---

## 🌍 Открыть в браузере

```
http://<IP_СЕРВЕРА>:8080
```

Замените `<IP_СЕРВЕРА>` на значение из `curl ifconfig.me`.

---
