# ⚽ FC Ironclad – Club Website

A full-stack football club website built with **Python Flask** and **MySQL**.

---

## Features

| Feature | Who can access |
|---|---|
| News feed (read) | Everyone |
| Post club updates | Logged-in members only |
| Download schedule as PNG | Everyone (no login required) |
| Admin panel (manage members, fixtures, results) | Admin members only |

---

## Tech Stack

- **Backend** – Python 3.11 + Flask
- **Database** – MySQL 8+ (falls back to SQLite automatically for local dev)
- **Image generation** – Pillow (schedule PNG)
- **Auth** – Session-based login with PBKDF2 password hashing (stdlib)
- **Frontend** – Server-rendered Jinja2 templates, pure CSS/HTML

---

## Quick Start

### 1 – Clone & install dependencies

```bash
pip install -r requirements.txt
```

### 2a – MySQL setup (production)

```bash
# Create the database and tables
mysql -u root -p < schema.sql
```

Set environment variables:

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=fc_user
export DB_PASSWORD=yourpassword
export DB_NAME=fc_ironclad
export SECRET_KEY=change-me-to-something-random
```

### 2b – SQLite (development / demo)

No configuration needed — SQLite kicks in automatically if `mysql-connector-python`
is not installed or MySQL is unreachable. A file `fc_ironclad.db` is created in
the project directory.

### 3 – Run

```bash
python app.py
# → http://localhost:5000
```

---

## Default credentials

| Username | Password | Role |
|---|---|---|
| admin | admin123 | admin |

**Change the admin password immediately after first login** via the admin panel.

---

## Project Structure

```
football_club/
├── app.py               # Flask routes & application entry point
├── db.py                # All database queries (MySQL + SQLite)
├── schedule_image.py    # PNG schedule generator (Pillow)
├── schema.sql           # MySQL DDL + seed data
├── requirements.txt
├── templates/
│   ├── base.html        # Nav, layout, CSS design system
│   ├── index.html       # Public news feed
│   ├── schedule.html    # Fixture schedule page
│   ├── login.html       # Member login
│   ├── new_post.html    # Post editor (members only)
│   └── admin.html       # Admin panel
└── README.md
```

---

## Switching to MySQL (from SQLite)

1. Install the driver:  `pip install mysql-connector-python`
2. Run `schema.sql` on your MySQL server
3. Set the `DB_*` environment variables shown above
4. Restart `app.py` — it will connect to MySQL automatically

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | localhost | MySQL host |
| `DB_PORT` | 3306 | MySQL port |
| `DB_USER` | root | MySQL user |
| `DB_PASSWORD` | *(empty)* | MySQL password |
| `DB_NAME` | fc_ironclad | Database name |
| `SQLITE_PATH` | fc_ironclad.db | SQLite file path (fallback) |
| `SECRET_KEY` | change-me… | Flask session secret |

---

## Schedule PNG

`GET /schedule/download` returns the full fixture list rendered as a 1080×auto PNG.
Anyone can download it — no authentication required.
The image is generated on-the-fly from live database data.

---

## Security notes for production

- Set `SECRET_KEY` to a long random string (`python -c "import secrets; print(secrets.token_hex(32))"`)
- Run behind nginx/gunicorn, not Flask dev server
- Use a dedicated MySQL user with only `SELECT/INSERT/UPDATE/DELETE` on `fc_ironclad`
- Enable HTTPS (Let's Encrypt / Certbot)
