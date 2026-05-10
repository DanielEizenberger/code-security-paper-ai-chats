# ⚽ FC Ironclad — Club Website

A complete, production-ready football club website with:

- **Public news feed** — visible to everyone
- **Member-only posting** — only registered club members can create news updates
- **MySQL + Flask** backend — all data stored persistently
- **Admin panel** — manage members (activate/deactivate, promote/demote)
- **Schedule page** — full season fixture list with results
- **One-click PNG download** — anyone on the internet can download the schedule as a styled image

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3.12 · Flask 3             |
| Database  | MySQL 8 · Flask-SQLAlchemy        |
| Auth      | Flask-Login · Flask-Bcrypt (bcrypt hashing) |
| Images    | Pillow (schedule PNG generation)  |
| Frontend  | Jinja2 templates · Vanilla CSS/JS |
| Deploy    | Docker + Docker Compose           |

---

## Quick Start (Docker — Recommended)

```bash
# 1. Clone / copy the project
cd football_club

# 2. Start both MySQL and the Flask app
docker compose up --build

# 3. Open http://localhost:5000
#    Register the first account → it becomes admin automatically
```

---

## Manual Setup (without Docker)

### 1. MySQL

```bash
mysql -u root -p < setup_db.sql
```

Or create the DB manually:
```sql
CREATE DATABASE football_club_db CHARACTER SET utf8mb4;
CREATE USER 'football_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON football_club_db.* TO 'football_user'@'localhost';
```

### 2. Python environment

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY and MySQL credentials
```

### 4. Run

```bash
flask run          # development
# or
gunicorn -w 4 "app:create_app()"   # production
```

---

## Project Structure

```
football_club/
├── app.py                  # App factory, extensions, DB seeding
├── models.py               # SQLAlchemy models (Member, NewsPost, ScheduleMatch)
├── schedule_image.py       # Pillow PNG generator
├── routes/
│   ├── auth.py             # /auth — register, login, logout, member management
│   ├── main.py             # /  — homepage, about
│   ├── news.py             # /news — CRUD posts
│   └── schedule.py         # /schedule — view, PNG download, admin manage
├── templates/
│   ├── base.html
│   ├── main/               # index.html, about.html
│   ├── auth/               # login.html, register.html, members.html
│   ├── news/               # index.html, detail.html, form.html
│   └── schedule/           # index.html, manage.html
├── static/
│   ├── css/style.css
│   └── js/main.js
├── setup_db.sql
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Database Schema

### `members`
| Column        | Type         | Notes                              |
|---------------|-------------|-------------------------------------|
| id            | INT PK       |                                     |
| username      | VARCHAR(64)  | unique                              |
| email         | VARCHAR(120) | unique                              |
| password_hash | VARCHAR(128) | bcrypt                              |
| display_name  | VARCHAR(100) |                                     |
| role          | VARCHAR(20)  | `member` or `admin`                 |
| joined_at     | DATETIME     |                                     |
| is_active     | BOOLEAN      | inactive members cannot log in      |

### `news_posts`
| Column     | Type         | Notes                               |
|------------|-------------|--------------------------------------|
| id         | INT PK       |                                      |
| title      | VARCHAR(200) |                                      |
| body       | TEXT         |                                      |
| category   | VARCHAR(50)  | General / Match Report / Transfer …  |
| pinned     | BOOLEAN      | pinned posts appear first            |
| author_id  | INT FK       | → members.id                         |
| created_at | DATETIME     |                                      |
| updated_at | DATETIME     | auto-updated on edit                 |

### `schedule_matches`
| Column      | Type        | Notes                               |
|-------------|------------|--------------------------------------|
| id          | INT PK      |                                      |
| date        | VARCHAR(10) | YYYY-MM-DD                           |
| time        | VARCHAR(5)  | HH:MM                                |
| opponent    | VARCHAR(100)|                                      |
| location    | VARCHAR(10) | `Home` or `Away`                     |
| competition | VARCHAR(50) | League / Cup …                       |
| result      | VARCHAR(20) | nullable — e.g. `2-1`               |

---

## Access Control Summary

| Route                   | Public | Member | Admin |
|-------------------------|--------|--------|-------|
| Homepage                | ✅     | ✅     | ✅    |
| News feed (read)        | ✅     | ✅     | ✅    |
| Schedule (view)         | ✅     | ✅     | ✅    |
| Schedule download (PNG) | ✅     | ✅     | ✅    |
| Post news               | ❌     | ✅     | ✅    |
| Edit/delete own post    | ❌     | ✅     | ✅    |
| Edit/delete any post    | ❌     | ❌     | ✅    |
| Member management       | ❌     | ❌     | ✅    |
| Manage schedule         | ❌     | ❌     | ✅    |

---

## First-Run Notes

- The **first registered user** is automatically assigned the `admin` role.
- 10 sample fixtures are seeded into the schedule on first startup.
- To reset the schedule, truncate the `schedule_matches` table and restart.

---

## Production Checklist

- [ ] Change `SECRET_KEY` to a long random string (`python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Use a strong MySQL password
- [ ] Put an Nginx reverse proxy in front of Gunicorn
- [ ] Enable HTTPS (Let's Encrypt / Certbot)
- [ ] Set `FLASK_ENV=production`
- [ ] Back up the MySQL volume regularly
