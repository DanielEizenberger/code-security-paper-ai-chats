# ⚽ FC Ironwall — Club Website

A production-ready football club website built with **Python Flask** + **MySQL**.

## Features

| Feature | Who can access |
|---|---|
| Homepage with news feed | Everyone |
| Full news archive with category filter | Everyone |
| Read individual posts | Everyone |
| Download match schedule as PNG | Everyone |
| Write / delete posts | Logged-in members only |
| View members directory | Logged-in members only |
| Register new account | Invite-code holders only |

---

## Project Structure

```
football_club/
├── app.py                # Flask application & routes
├── schedule_image.py     # Pillow PNG schedule generator
├── seed.py               # One-time DB seed (admin user + sample posts)
├── schema.sql            # MySQL schema + fixture data
├── requirements.txt
├── Dockerfile
├── docker-compose.yml    # ← easiest way to run
├── entrypoint.sh
└── templates/
    ├── base.html
    ├── index.html
    ├── news.html
    ├── view_post.html
    ├── create_post.html
    ├── schedule.html
    ├── login.html
    ├── register.html
    ├── members.html
    └── 404.html
```

---

## Quick Start (Docker — recommended)

### Prerequisites
- Docker Desktop (or Docker + Compose)

### Steps

```bash
# 1. Clone / copy this folder
cd football_club

# 2. (Optional) Change secrets in docker-compose.yml:
#    SECRET_KEY, INVITE_CODE, MYSQL_PASSWORD

# 3. Start everything
docker compose up --build

# 4. Open http://localhost:5000
```

The `entrypoint.sh` automatically runs `seed.py` on first start,
creating the admin account and sample posts.

**Default admin credentials** (change immediately!):
- Email: `admin@fcironwall.com`
- Password: `Admin1234!`

**Default invite code**: `IRONWALL2024`

---

## Manual Setup (without Docker)

### 1. MySQL

```sql
-- As root:
CREATE USER 'fcuser'@'localhost' IDENTIFIED BY 'fcpassword';
GRANT ALL ON football_club.* TO 'fcuser'@'localhost';
FLUSH PRIVILEGES;

mysql -u fcuser -pfcpassword < schema.sql
```

### 2. Python environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment variables

```bash
export MYSQL_HOST=localhost
export MYSQL_USER=fcuser
export MYSQL_PASSWORD=fcpassword
export MYSQL_DB=football_club
export SECRET_KEY="your-very-secret-key"
export INVITE_CODE="YOURCODE"
```

### 4. Seed & run

```bash
python seed.py           # creates admin + sample posts
python app.py            # dev server on http://localhost:5000

# Production:
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

---

## Configuration Reference

| Env var | Default | Description |
|---|---|---|
| `MYSQL_HOST` | `localhost` | DB hostname |
| `MYSQL_USER` | `fcuser` | DB username |
| `MYSQL_PASSWORD` | `fcpassword` | DB password |
| `MYSQL_DB` | `football_club` | Database name |
| `SECRET_KEY` | hardcoded dev key | Flask session secret |
| `INVITE_CODE` | `IRONWALL2024` | Code required to register |

---

## Schedule PNG Download

`GET /schedule/download`

Returns a ready-to-share 1100×px PNG of all fixtures, generated with Pillow.
No authentication required — anyone can download it.

---

## Security Notes for Production

1. **Change `SECRET_KEY`** to a long random string (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
2. **Change `INVITE_CODE`** and give it only to new players personally
3. **Change the admin password** via the DB directly after first login:
   ```python
   from werkzeug.security import generate_password_hash
   print(generate_password_hash('YourNewPassword'))
   ```
4. Put the app behind **Nginx + HTTPS** (Let's Encrypt / Certbot)
5. Use a **strong MySQL password** in production
6. Set `debug=False` in Flask (already the case when run via gunicorn)
