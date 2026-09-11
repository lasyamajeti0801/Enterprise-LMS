# Enterprise Learning Management System - Deployment Guide

This guide details how to deploy the Enterprise LMS into production environments using WSGI servers such as **Gunicorn** (Linux/macOS) or **Waitress** (Windows), along with reverse proxy configuration via **Nginx**.

---

## 🏗️ Production Architecture

```
[ Clients / Browsers ]
          |
          v HTTPS (Port 443)
[ Nginx Reverse Proxy & Static Asset Server ]
          |
          v WSGI Unix Socket or Local Port (e.g., 127.0.0.1:8000)
[ WSGI Server: Gunicorn / Waitress ]
          |
[ Flask Application Factory (create_app("production")) ]
          |
[ Database: PostgreSQL / SQLite (lms_prod.db) ]
```

---

## 🐧 1. Linux Production Deployment (Gunicorn + Systemd)

### Step 1: Install Production Dependencies
```bash
pip install gunicorn psycopg2-binary
```

### Step 2: Configure Environment Variables
Create `/etc/lms.env`:
```ini
LMS_ENV=production
SECRET_KEY=generate-a-strong-64-character-random-hex-string
DATABASE_URL=postgresql://lms_user:secure_password@localhost:5432/lms_prod
PORT=8000
```

### Step 3: Create Systemd Service File
Create `/etc/systemd/system/lms.service`:
```ini
[Unit]
Description=Enterprise Learning Management System WSGI Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/lms
EnvironmentFile=/etc/lms.env
ExecStart=/var/www/lms/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 "app:create_app('production')"
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 4: Start and Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl start lms
sudo systemctl enable lms
```

---

## 🪟 2. Windows Server Deployment (Waitress)

### Step 1: Install Waitress
```powershell
pip install waitress
```

### Step 2: Launch with Production WSGI
```powershell
python -c "from waitress import serve; from app import create_app; serve(create_app('production'), host='0.0.0.0', port=5000, threads=8)"
```

---

## 🌐 3. Nginx Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name lms.yourinstitution.edu;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name lms.yourinstitution.edu;

    ssl_certificate /etc/letsencrypt/live/lms.yourinstitution.edu/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lms.yourinstitution.edu/privkey.pem;

    client_max_body_size 25M;

    # Static Assets Cache
    location /static/ {
        alias /var/www/lms/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Proxy to WSGI App
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
