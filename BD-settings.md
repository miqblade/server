# Установка и настройка pgAdmin 4 (Web-mode) на Debian/Ubuntu сервере (GCP)

## 📦 Установка pgAdmin 4

```bash
sudo apt update
sudo apt install curl ca-certificates gnupg apache2 -y
```

Добавляем ключ и репозиторий:

```bash
curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | gpg --dearmor | sudo tee /usr/share/keyrings/pgadmin-keyring.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/pgadmin-keyring.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/debian $(lsb_release -cs) pgadmin4" | sudo tee /etc/apt/sources.list.d/pgadmin4.list

sudo apt update
```

Устанавливаем pgAdmin 4 (web + server):

```bash
sudo apt install pgadmin4-web pgadmin4-server -y
```

---

## ⚙️ Настройка pgAdmin 4 в Web-режиме

Запускаем скрипт и указываем email/пароль администратора:

```bash
sudo /usr/pgadmin4/bin/setup-web.sh
```

На экране будет запрос:

```
Email address: admin@admin.com
Password: ********
Retype password: ********
```

---

## 🌐 Доступ к веб-интерфейсу

По умолчанию pgAdmin запускается под **Apache** и доступен по адресу:

```
http://<IP-сервера>/pgadmin4
```

Проверь статус Apache:

```bash
sudo systemctl status apache2
```

Если не запущен:

```bash
sudo systemctl start apache2
sudo systemctl enable apache2
```

---

## 🔥 Открытие порта в GCP

Перейди в раздел **"VPC Network → Firewall rules"** и создай новое правило:

- Name: `allow-http`
- Direction: `Ingress`
- Action: `Allow`
- Targets: `All instances in the network`
- Source IP ranges: `0.0.0.0/0`
- Protocols and ports: `tcp:80`

---

## 🟢 Автозапуск pgAdmin и Apache

Apache запускается автоматически вместе с системой:

```bash
sudo systemctl enable apache2
```

---

## 🧠 Проверка

Открой в браузере:

```
http://<твой-сервер>/pgadmin4
```

Введи логин/пароль, указанный при `setup-web.sh`, и начни использовать pgAdmin 4.

---

## 📌 Где хранятся данные?

- Конфигурация: `/usr/pgadmin4/`
- Apache site config: `/etc/apache2/conf-available/pgadmin4.conf`
- База настроек: `~/.pgadmin`

---
