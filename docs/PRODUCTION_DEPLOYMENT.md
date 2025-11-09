# Production Deployment Guide

## Overview

This comprehensive guide covers the complete deployment process for the Rezervasyon Yönetim Sistemi (Reservation Management System) in a production environment. It includes SSL/TLS setup, web server configuration, database security, monitoring, backup procedures, and security hardening.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [SSL/TLS Certificate Setup](#ssltls-certificate-setup)
4. [Web Server Configuration](#web-server-configuration)
5. [Application Deployment](#application-deployment)
6. [Database Setup and Security](#database-setup-and-security)
7. [Redis Configuration](#redis-configuration)
8. [Environment Variables](#environment-variables)
9. [Security Hardening](#security-hardening)
10. [Monitoring and Logging](#monitoring-and-logging)
11. [Backup and Recovery](#backup-and-recovery)
12. [Performance Optimization](#performance-optimization)
13. [Deployment Checklist](#deployment-checklist)
14. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum:**
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 20 GB SSD
- **OS:** Ubuntu 20.04/22.04 LTS or similar

**Recommended:**
- **CPU:** 4+ cores
- **RAM:** 8+ GB
- **Disk:** 50+ GB SSD
- **OS:** Ubuntu 22.04 LTS

### Required Software

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install prerequisites
sudo apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    supervisor
```

### Domain and DNS

- Domain name registered (e.g., `rezervasyon.example.com`)
- DNS A record pointing to your server IP
- Wait for DNS propagation (can take up to 48 hours)

```bash
# Verify DNS
dig rezervasyon.example.com +short
# Should return your server's IP address
```

## Server Setup

### 1. Create Application User

```bash
# Create dedicated user for the application
sudo useradd -m -s /bin/bash rezervasyon
sudo usermod -aG sudo rezervasyon

# Switch to application user
sudo su - rezervasyon
```

### 2. Set Up Directory Structure

```bash
# Create directory structure
mkdir -p ~/app
mkdir -p ~/app/logs
mkdir -p ~/app/backups
mkdir -p ~/app/uploads

# Set proper permissions
chmod 755 ~/app
chmod 750 ~/app/logs
chmod 700 ~/app/backups
```

### 3. Clone Application

```bash
cd ~/app
git clone https://github.com/your-org/rezervation.git
cd rezervation

# Or upload files via scp/sftp
```

## SSL/TLS Certificate Setup

### Option 1: Let's Encrypt (Free, Recommended)

**Step 1: Install Certbot**
```bash
sudo apt-get install certbot python3-certbot-nginx
```

**Step 2: Obtain Certificate**
```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d rezervasyon.example.com

# Certificate locations:
# - Certificate: /etc/letsencrypt/live/rezervasyon.example.com/fullchain.pem
# - Private Key: /etc/letsencrypt/live/rezervasyon.example.com/privkey.pem
```

**Step 3: Auto-renewal**
```bash
# Test renewal
sudo certbot renew --dry-run

# Set up automatic renewal (cron job)
sudo crontab -e

# Add this line:
0 0 * * 0 certbot renew --quiet --post-hook "systemctl reload nginx"
```

### Option 2: Commercial Certificate

**Step 1: Generate CSR**
```bash
# Generate private key
sudo openssl genrsa -out /etc/ssl/private/rezervasyon.key 2048

# Generate CSR
sudo openssl req -new -key /etc/ssl/private/rezervasyon.key \
    -out /etc/ssl/certs/rezervasyon.csr

# Submit CSR to Certificate Authority
```

**Step 2: Install Certificate**
```bash
# Place certificate files
sudo cp your-certificate.crt /etc/ssl/certs/rezervasyon.crt
sudo cp intermediate-ca.crt /etc/ssl/certs/intermediate.crt

# Combine certificates
sudo cat /etc/ssl/certs/rezervasyon.crt \
    /etc/ssl/certs/intermediate.crt > \
    /etc/ssl/certs/rezervasyon-chain.crt
```

### Certificate Verification

```bash
# Verify certificate
sudo openssl x509 -in /etc/letsencrypt/live/rezervasyon.example.com/fullchain.pem \
    -noout -text

# Check expiration
sudo openssl x509 -in /etc/letsencrypt/live/rezervasyon.example.com/fullchain.pem \
    -noout -dates
```

## Web Server Configuration

### Nginx Configuration

**Step 1: Create Nginx Configuration**
```bash
sudo nano /etc/nginx/sites-available/rezervasyon
```

**Step 2: Configuration File**
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name rezervasyon.example.com;
    
    # Let's Encrypt challenge
    location ^~ /.well-known/acme-challenge/ {
        allow all;
        root /var/www/html;
    }
    
    # Redirect all other HTTP traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name rezervasyon.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/rezervasyon.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rezervasyon.example.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS (managed by Flask app, but can add here as well)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/rezervasyon.example.com/chain.pem;

    # Security Headers (additional layer, Flask also sets these)
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Client body size (for file uploads)
    client_max_body_size 16M;

    # Logging
    access_log /var/log/nginx/rezervasyon-access.log;
    error_log /var/log/nginx/rezervasyon-error.log;

    # Static files
    location /static {
        alias /home/rezervasyon/app/rezervation/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Uploaded files
    location /uploads {
        alias /home/rezervasyon/app/rezervation/app/static/uploads;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy to Flask application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting (additional layer)
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    
    location /auth/login {
        limit_req zone=login burst=10 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

**Step 3: Enable Site**
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/rezervasyon /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Alternative: Apache Configuration

```apache
<VirtualHost *:80>
    ServerName rezervasyon.example.com
    Redirect permanent / https://rezervasyon.example.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName rezervasyon.example.com

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/rezervasyon.example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/rezervasyon.example.com/privkey.pem
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder off

    # HSTS
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

    # Static files
    Alias /static /home/rezervasyon/app/rezervation/app/static
    <Directory /home/rezervasyon/app/rezervation/app/static>
        Require all granted
    </Directory>

    # Proxy to Flask
    ProxyPass /static !
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    RequestHeader set X-Forwarded-Proto "https"

    ErrorLog ${APACHE_LOG_DIR}/rezervasyon-error.log
    CustomLog ${APACHE_LOG_DIR}/rezervasyon-access.log combined
</VirtualHost>
```

## Application Deployment

### 1. Set Up Python Virtual Environment

```bash
cd /home/rezervasyon/app/rezervation

# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install production server (Gunicorn)
pip install gunicorn gevent
```

### 3. Create Environment File

```bash
# Create .env file
nano .env
```

```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=<generate-with-secrets-token-hex-32>
JWT_SECRET_KEY=<generate-with-secrets-token-hex-32>

# Database
DATABASE_URL=postgresql://rezervasyon:password@localhost/rezervasyon_db

# Redis
REDIS_URL=redis://:redis-password@localhost:6379/0

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
HSTS_ENABLED=true
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=true

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://:redis-password@localhost:6379/1

# File Upload
UPLOAD_FOLDER=/home/rezervasyon/app/rezervation/app/static/uploads
MAX_CONTENT_LENGTH=16777216

# CSRF Protection
WTF_CSRF_ENABLED=true
```

**Generate Secret Keys:**
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

### 4. Initialize Database

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
flask db upgrade

# Seed initial data (if needed)
python seed_data.py
```

### 5. Set Up Gunicorn

**Create Gunicorn configuration:**
```bash
nano gunicorn_config.py
```

```python
# gunicorn_config.py
import multiprocessing

# Server Socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = '/home/rezervasyon/app/logs/gunicorn-access.log'
errorlog = '/home/rezervasyon/app/logs/gunicorn-error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = 'rezervasyon'

# Server Mechanics
daemon = False  # Supervisor will handle daemonization
pidfile = '/home/rezervasyon/app/gunicorn.pid'
user = 'rezervasyon'
group = 'rezervasyon'
umask = 0o007
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

### 6. Set Up Supervisor

**Create Supervisor configuration:**
```bash
sudo nano /etc/supervisor/conf.d/rezervasyon.conf
```

```ini
[program:rezervasyon]
command=/home/rezervasyon/app/rezervation/venv/bin/gunicorn -c /home/rezervasyon/app/rezervation/gunicorn_config.py run:app
directory=/home/rezervasyon/app/rezervation
user=rezervasyon
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/rezervasyon/app/logs/supervisor.log
stderr_logfile=/home/rezervasyon/app/logs/supervisor-error.log
environment=PATH="/home/rezervasyon/app/rezervation/venv/bin"
```

**Start application:**
```bash
# Update Supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start application
sudo supervisorctl start rezervasyon

# Check status
sudo supervisorctl status rezervasyon
```

## Database Setup and Security

### PostgreSQL Installation and Configuration

**Step 1: Install PostgreSQL**
```bash
sudo apt-get install postgresql postgresql-contrib
```

**Step 2: Secure PostgreSQL**
```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/14/main/postgresql.conf
```

```conf
# Listen only on localhost (if database on same server)
listen_addresses = 'localhost'

# Connection limits
max_connections = 100

# Memory settings (adjust based on your server)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 7864kB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

**Step 3: Configure Authentication**
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             postgres                                peer
local   all             all                                     peer

# IPv4 local connections
host    rezervasyon_db  rezervasyon     127.0.0.1/32            scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256

# IPv6 local connections
host    all             all             ::1/128                 scram-sha-256
```

**Step 4: Create Database and User**
```bash
# Switch to postgres user
sudo -u postgres psql

# Create user
CREATE USER rezervasyon WITH PASSWORD 'strong-password-here';

# Create database
CREATE DATABASE rezervasyon_db OWNER rezervasyon;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE rezervasyon_db TO rezervasyon;

# Exit
\q
```

**Step 5: Test Connection**
```bash
psql -h localhost -U rezervasyon -d rezervasyon_db
```

### Database Security Best Practices

1. **Strong Passwords:**
```bash
# Generate strong database password
openssl rand -base64 32
```

2. **Regular Backups:**
```bash
# Create backup script
sudo nano /home/rezervasyon/app/backup-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/rezervasyon/app/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/rezervasyon_db_$TIMESTAMP.sql.gz"

# Create backup
pg_dump -h localhost -U rezervasyon rezervasyon_db | gzip > $BACKUP_FILE

# Keep only last 30 days of backups
find $BACKUP_DIR -name "rezervasyon_db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

```bash
# Make executable
chmod +x /home/rezervasyon/app/backup-db.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /home/rezervasyon/app/backup-db.sh >> /home/rezervasyon/app/logs/backup.log 2>&1
```

3. **SSL Connections (if database on separate server):**
```bash
# Generate SSL certificates for PostgreSQL
sudo -u postgres openssl req -new -x509 -days 365 -nodes \
    -out /var/lib/postgresql/14/main/server.crt \
    -keyout /var/lib/postgresql/14/main/server.key

sudo chmod 600 /var/lib/postgresql/14/main/server.key
sudo chown postgres:postgres /var/lib/postgresql/14/main/server.*

# Enable SSL in postgresql.conf
ssl = on
ssl_cert_file = '/var/lib/postgresql/14/main/server.crt'
ssl_key_file = '/var/lib/postgresql/14/main/server.key'
```

## Redis Configuration

### Installation and Security

**Step 1: Install Redis**
```bash
sudo apt-get install redis-server
```

**Step 2: Configure Redis**
```bash
sudo nano /etc/redis/redis.conf
```

```conf
# Bind to localhost only (if on same server)
bind 127.0.0.1

# Require password
requirepass your-strong-redis-password-here

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# Persistence
save 900 1      # Save after 15 minutes if 1 key changed
save 300 10     # Save after 5 minutes if 10 keys changed
save 60 10000   # Save after 1 minute if 10000 keys changed

# Max memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
```

**Step 3: Restart Redis**
```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

**Step 4: Test Redis**
```bash
redis-cli -a your-redis-password ping
# Should return: PONG
```

### Redis Security Best Practices

1. **Firewall Rules:**
```bash
# Block external access to Redis port
sudo ufw deny 6379
```

2. **TLS/SSL (if Redis on separate server):**
```bash
# Generate certificates
sudo openssl genrsa -out /etc/redis/redis.key 2048
sudo openssl req -new -x509 -key /etc/redis/redis.key \
    -out /etc/redis/redis.crt -days 365

# Configure Redis for TLS
tls-port 6379
port 0
tls-cert-file /etc/redis/redis.crt
tls-key-file /etc/redis/redis.key
tls-auth-clients no
```

## Environment Variables

### Secure Environment Management

**Never commit .env to version control:**
```bash
# .gitignore
.env
.env.production
*.env.local
```

**Production .env template:**
```bash
# ===============================
# Flask Configuration
# ===============================
FLASK_APP=run.py
FLASK_ENV=production

# ===============================
# Secret Keys (CRITICAL)
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
# ===============================
SECRET_KEY=
JWT_SECRET_KEY=

# ===============================
# Database
# ===============================
DATABASE_URL=postgresql://user:password@localhost/dbname

# ===============================
# Redis
# ===============================
REDIS_URL=redis://:password@localhost:6379/0

# ===============================
# Security Settings
# ===============================
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

HSTS_ENABLED=true
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=true

WTF_CSRF_ENABLED=true

# ===============================
# Rate Limiting
# ===============================
RATELIMIT_STORAGE_URL=redis://:password@localhost:6379/1

# ===============================
# File Upload
# ===============================
UPLOAD_FOLDER=/path/to/uploads
MAX_CONTENT_LENGTH=16777216

# ===============================
# Email (Optional)
# ===============================
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=

# ===============================
# Monitoring (Optional)
# ===============================
SENTRY_DSN=
```

### Setting Environment Variables

**Option 1: .env File (Recommended)**
```bash
# Application reads from .env automatically
# Ensure .env is not readable by other users
chmod 600 .env
```

**Option 2: Supervisor Environment**
```ini
[program:rezervasyon]
environment=
    SECRET_KEY="your-secret-key",
    DATABASE_URL="postgresql://...",
    REDIS_URL="redis://..."
```

**Option 3: Export in Shell**
```bash
# Add to ~/.bashrc or ~/.profile
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://..."
```

## Security Hardening

### Firewall Configuration

```bash
# Enable firewall
sudo ufw enable

# Allow SSH (change port if using non-standard)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status verbose
```

### SSH Hardening

```bash
sudo nano /etc/ssh/sshd_config
```

```conf
# Disable root login
PermitRootLogin no

# Use key-based authentication only
PasswordAuthentication no
PubkeyAuthentication yes

# Change default port (optional)
Port 2222

# Disable empty passwords
PermitEmptyPasswords no

# Limit authentication attempts
MaxAuthTries 3

# Set login timeout
LoginGraceTime 30
```

```bash
sudo systemctl restart sshd
```

### File Permissions

```bash
# Application files
sudo chown -R rezervasyon:rezervasyon /home/rezervasyon/app
sudo chmod -R 750 /home/rezervasyon/app

# Logs
sudo chmod 750 /home/rezervasyon/app/logs
sudo chmod 640 /home/rezervasyon/app/logs/*.log

# Uploads
sudo chmod 755 /home/rezervasyon/app/rezervation/app/static/uploads

# .env file (critical)
sudo chmod 600 /home/rezervasyon/app/rezervation/.env

# SSL certificates
sudo chmod 600 /etc/letsencrypt/archive/*/privkey*.pem
```

### Automatic Security Updates

```bash
# Install unattended-upgrades
sudo apt-get install unattended-upgrades

# Configure
sudo dpkg-reconfigure --priority=low unattended-upgrades

# Enable automatic updates for security patches
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
```

### Intrusion Detection

```bash
# Install fail2ban
sudo apt-get install fail2ban

# Configure
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Monitoring and Logging

### Application Logging

**Configure logging in `app/__init__.py`:**
```python
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # ... existing configuration ...
    
    # Production logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Application log
        file_handler = RotatingFileHandler(
            'logs/rezervasyon.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Rezervasyon startup')
    
    return app
```

### System Monitoring with Prometheus

**Install Prometheus:**
```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-*/prometheus /usr/local/bin/
sudo mv prometheus-*/promtool /usr/local/bin/

# Create configuration
sudo nano /etc/prometheus/prometheus.yml
```

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
  
  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']
```

### Log Rotation

```bash
sudo nano /etc/logrotate.d/rezervasyon
```

```conf
/home/rezervasyon/app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 rezervasyon rezervasyon
    sharedscripts
    postrotate
        /usr/bin/supervisorctl restart rezervasyon > /dev/null
    endscript
}
```

### Health Check Endpoint

**Add to Flask app:**
```python
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database
        db.session.execute('SELECT 1')
        
        # Check Redis
        from redis import Redis
        r = Redis.from_url(app.config['REDIS_URL'])
        r.ping()
        
        return jsonify({
            'status': 'healthy',
            'database': 'ok',
            'redis': 'ok'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

**Monitor with cron:**
```bash
# Add to crontab
*/5 * * * * curl -f https://rezervasyon.example.com/health || echo "Health check failed" | mail -s "Alert" admin@example.com
```

## Backup and Recovery

### Automated Backup Strategy

**1. Database Backups:**
```bash
#!/bin/bash
# /home/rezervasyon/app/scripts/backup.sh

# Configuration
BACKUP_DIR="/home/rezervasyon/app/backups/db"
S3_BUCKET="s3://rezervasyon-backups"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup database
pg_dump -h localhost -U rezervasyon rezervasyon_db | \
    gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_$TIMESTAMP.sql.gz $S3_BUCKET/db/

# Clean old backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: db_$TIMESTAMP.sql.gz"
```

**2. Application Files:**
```bash
#!/bin/bash
# /home/rezervasyon/app/scripts/backup-files.sh

BACKUP_DIR="/home/rezervasyon/app/backups/files"
APP_DIR="/home/rezervasyon/app/rezervation"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup uploaded files
tar -czf $BACKUP_DIR/uploads_$TIMESTAMP.tar.gz \
    $APP_DIR/app/static/uploads/

# Clean old backups
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +30 -delete
```

**3. Schedule Backups:**
```bash
# Add to crontab
crontab -e

# Database backup daily at 2 AM
0 2 * * * /home/rezervasyon/app/scripts/backup.sh

# File backup daily at 3 AM
0 3 * * * /home/rezervasyon/app/scripts/backup-files.sh

# Weekly full backup (Sunday 4 AM)
0 4 * * 0 /home/rezervasyon/app/scripts/full-backup.sh
```

### Disaster Recovery Procedure

**1. Restore Database:**
```bash
# Stop application
sudo supervisorctl stop rezervasyon

# Drop and recreate database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS rezervasyon_db;"
sudo -u postgres psql -c "CREATE DATABASE rezervasyon_db OWNER rezervasyon;"

# Restore from backup
gunzip < /path/to/backup/db_20240115_020000.sql.gz | \
    psql -h localhost -U rezervasyon rezervasyon_db

# Start application
sudo supervisorctl start rezervasyon
```

**2. Restore Application Files:**
```bash
# Extract backup
tar -xzf /path/to/backup/uploads_20240115_030000.tar.gz \
    -C /home/rezervasyon/app/rezervation/app/static/

# Fix permissions
sudo chown -R rezervasyon:rezervasyon \
    /home/rezervasyon/app/rezervation/app/static/uploads
sudo chmod -R 755 /home/rezervasyon/app/rezervation/app/static/uploads
```

## Performance Optimization

### Gunicorn Tuning

```python
# gunicorn_config.py

# Worker formula: (2 x CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Use gevent for async I/O
worker_class = 'gevent'

# Worker connections
worker_connections = 1000

# Request timeouts
timeout = 30
graceful_timeout = 30

# Worker recycling
max_requests = 1000
max_requests_jitter = 50
```

### Database Optimization

**1. Connection Pooling:**
```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

**2. Database Indexes:**
```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_reservations_event_id ON reservations(event_id);
CREATE INDEX idx_events_company_id ON events(company_id);
CREATE INDEX idx_events_date ON events(event_date);
```

**3. Query Optimization:**
```python
# Use eager loading to avoid N+1 queries
events = Event.query.options(
    db.joinedload(Event.company),
    db.joinedload(Event.reservations)
).all()
```

### Redis Optimization

```conf
# /etc/redis/redis.conf

# Memory optimization
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence tuning
save 900 1
save 300 10
save 60 10000

# Disable RDB snapshots if using AOF
# save ""

# Enable AOF for better durability
appendonly yes
appendfsync everysec
```

### Nginx Caching

```nginx
# Add to nginx configuration
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Cache responses from Flask
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app_cache:10m inactive=60m;

location / {
    proxy_cache app_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_bypass $http_cache_control;
    add_header X-Cache-Status $upstream_cache_status;
    
    proxy_pass http://127.0.0.1:5000;
    # ... other proxy settings ...
}
```

## Deployment Checklist

### Pre-Deployment

- [ ] SSL certificate obtained and configured
- [ ] Domain DNS pointing to server
- [ ] Server firewall configured
- [ ] PostgreSQL installed and secured
- [ ] Redis installed and secured
- [ ] Nginx/Apache installed and configured
- [ ] Application user created
- [ ] Directory structure created
- [ ] Strong SECRET_KEY and JWT_SECRET_KEY generated
- [ ] Environment variables configured (.env file)
- [ ] All required Python packages installed

### Security

- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `SESSION_COOKIE_HTTPONLY = True`
- [ ] `SESSION_COOKIE_SAMESITE = 'Lax'`
- [ ] HSTS enabled (`HSTS_ENABLED = True`)
- [ ] CSP configured (production mode)
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled
- [ ] SSH key-based authentication only
- [ ] Firewall rules configured
- [ ] fail2ban installed and configured
- [ ] File permissions set correctly
- [ ] Database password strong and secure
- [ ] Redis password configured

### Application

- [ ] Database migrations run (`flask db upgrade`)
- [ ] Static files accessible
- [ ] Upload directory created and writable
- [ ] Gunicorn configured
- [ ] Supervisor configured
- [ ] Application starts successfully
- [ ] Health check endpoint working
- [ ] Logging configured
- [ ] Error handling tested

### Monitoring and Backups

- [ ] Log rotation configured
- [ ] Database backup script created
- [ ] File backup script created
- [ ] Backup schedule configured (cron jobs)
- [ ] Health check monitoring set up
- [ ] SSL certificate auto-renewal configured
- [ ] Security logs monitored
- [ ] Disk space monitoring configured

### Testing

- [ ] HTTPS working (no certificate errors)
- [ ] HTTP redirects to HTTPS
- [ ] Login functionality working
- [ ] File upload working
- [ ] Database queries working
- [ ] Redis sessions working
- [ ] Rate limiting working
- [ ] CSP not blocking legitimate resources
- [ ] All security headers present
- [ ] Performance acceptable under load

## Troubleshooting

### Application Won't Start

**Check Supervisor logs:**
```bash
sudo tail -f /home/rezervasyon/app/logs/supervisor-error.log
```

**Common issues:**
1. Port already in use
2. Database connection failed
3. Redis connection failed
4. Missing environment variables
5. Python dependencies not installed

### SSL Certificate Issues

**Certificate not trusted:**
```bash
# Check certificate chain
openssl s_client -connect rezervasyon.example.com:443 -showcerts

# Verify certificate
sudo certbot certificates
```

**Certificate renewal failed:**
```bash
# Manual renewal
sudo certbot renew --force-renewal

# Check renewal logs
sudo cat /var/log/letsencrypt/letsencrypt.log
```

### Database Connection Issues

**Test connection:**
```bash
psql -h localhost -U rezervasyon -d rezervasyon_db
```

**Common issues:**
1. Wrong password in DATABASE_URL
2. PostgreSQL not running
3. pg_hba.conf misconfigured
4. Firewall blocking connection

### Redis Connection Issues

**Test Redis:**
```bash
redis-cli -a your-password ping
```

**Common issues:**
1. Redis not running
2. Wrong password in REDIS_URL
3. Redis bound to wrong interface
4. Firewall blocking connection

### Performance Issues

**Check server resources:**
```bash
# CPU and memory
htop

# Disk usage
df -h

# Disk I/O
iotop
```

**Check application logs:**
```bash
tail -f /home/rezervasyon/app/logs/gunicorn-error.log
tail -f /home/rezervasyon/app/logs/rezervasyon.log
```

**Slow queries:**
```sql
-- Enable slow query log in PostgreSQL
ALTER DATABASE rezervasyon_db SET log_min_duration_statement = 1000;

-- Check slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

### Security Issues

**Check for failed login attempts:**
```bash
grep "FAILED LOGIN" /home/rezervasyon/app/logs/security.log
```

**Check CSP violations:**
```bash
grep "csp_violation" /home/rezervasyon/app/logs/security_events.json | tail -20
```

**Check rate limit violations:**
```bash
grep "rate_limit_exceeded" /home/rezervasyon/app/logs/security_events.json
```

## Support and Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor application logs
- Check disk space
- Verify backups completed

**Weekly:**
- Review security logs
- Check for software updates
- Monitor system performance
- Test backup restoration

**Monthly:**
- Review and rotate logs
- Update dependencies (after testing)
- Security audit
- Performance optimization review

### Updating the Application

```bash
# 1. Backup current version
cd /home/rezervasyon/app/rezervation
tar -czf ../backup_$(date +%Y%m%d).tar.gz .

# 2. Pull latest code
git pull origin main

# 3. Activate virtual environment
source venv/bin/activate

# 4. Update dependencies
pip install -r requirements.txt

# 5. Run migrations
flask db upgrade

# 6. Restart application
sudo supervisorctl restart rezervasyon

# 7. Verify
sudo supervisorctl status rezervasyon
curl https://rezervasyon.example.com/health
```

### Emergency Contacts

Document key contacts for production issues:

- **System Administrator:** 
- **Database Administrator:**
- **Security Team:**
- **Hosting Provider Support:**
- **SSL Certificate Provider:**

### Additional Resources

- [OWASP Production SCA](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Security Best Practices](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [Redis Security](https://redis.io/topics/security)

---

**Last Updated:** 2024-01-15
**Version:** 1.0
**Maintainer:** Security Team
