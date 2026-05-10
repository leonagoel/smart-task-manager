# TaskFlow — Smart Task Management System

A full-stack Python web application built with Flask, PostgreSQL, WebSockets, Pandas/NumPy analytics, and a responsive dark-themed UI.

---

## Features

- **Authentication** — Register, login, logout with secure password hashing (Werkzeug)
- **Task CRUD** — Create, read, update, delete tasks via REST API
- **Priority & Status** — Filter and manage tasks by priority (low/medium/high) and status (pending/in_progress/done)
- **Analytics** — Real-time stats computed with Pandas & NumPy (completion %, priority breakdown, daily trend)
- **WebSockets** — Live task updates broadcast to all connected clients via Flask-SocketIO
- **Responsive UI** — Clean dark-themed dashboard with sidebar navigation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask 3.0 |
| Auth | Flask-Login, Werkzeug |
| Database | PostgreSQL 14+, psycopg2 |
| Analytics | Pandas 2.2, NumPy 1.26 |
| Real-time | Flask-SocketIO 5, Eventlet |
| Frontend | HTML5, CSS3, Vanilla JS, Socket.IO client |

---

## Project Structure

```
smart-task-manager/
├── app/
│   ├── __init__.py          # Flask app factory, extensions init
│   ├── auth/
│   │   └── routes.py        # /auth/register, /auth/login, /auth/logout
│   ├── tasks/
│   │   └── routes.py        # GET/POST/PUT/DELETE /api/tasks
│   ├── analytics/
│   │   ├── routes.py        # GET /api/analytics
│   │   └── service.py       # Pandas & NumPy computation
│   ├── websocket/
│   │   └── events.py        # Socket.IO event handlers
│   ├── models/
│   │   ├── db.py            # Connection pool, init_db()
│   │   ├── user.py          # User model + Flask-Login
│   │   └── task.py          # Task model with CRUD methods
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── index.html       # Main dashboard
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── schema.sql               # Database DDL for submission
├── config.py                # Config loaded from environment
├── run.py                   # App entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-task-manager.git
cd smart-task-manager
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

```bash
# Create database
psql -U postgres -c "CREATE DATABASE taskmanager;"

# Run schema
psql -U postgres -d taskmanager -f schema.sql
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
SECRET_KEY=your-very-secret-key-change-this
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/taskmanager
FLASK_DEBUG=false
```

### 6. Run the application

```bash
python run.py
```

Visit **http://localhost:5000** in your browser.

---

## REST API Reference

All task endpoints require authentication (session cookie).

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/api/register` | Register new user |
| POST | `/auth/api/login` | Login |
| POST | `/auth/api/logout` | Logout |

**Register body:**
```json
{ "username": "alice", "email": "alice@example.com", "password": "secret123" }
```

**Login body:**
```json
{ "email": "alice@example.com", "password": "secret123" }
```

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks` | Get all tasks (supports `?status=` and `?priority=`) |
| POST | `/api/tasks` | Create a task |
| PUT | `/api/tasks/<id>` | Update a task (partial update supported) |
| DELETE | `/api/tasks/<id>` | Delete a task |

**Task body (POST/PUT):**
```json
{
  "title": "Build REST API",
  "description": "Implement Flask routes",
  "priority": "high",
  "status": "pending"
}
```

**Priority values:** `low` | `medium` | `high`  
**Status values:** `pending` | `in_progress` | `done`

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/analytics` | Returns Pandas-computed task statistics |

**Response:**
```json
{
  "total": 10,
  "completed": 4,
  "pending": 3,
  "in_progress": 3,
  "completion_pct": 40.0,
  "by_priority": { "high": 3, "medium": 5, "low": 2 },
  "by_status": { "pending": 3, "in_progress": 3, "done": 4 },
  "daily_counts": [{ "date": "2024-05-01", "count": 2 }]
}
```

---

## WebSocket Events

The server emits these events after any task mutation:

| Event | Payload | When |
|---|---|---|
| `task_created` | Task object | After POST /api/tasks |
| `task_updated` | Task object | After PUT /api/tasks/<id> |
| `task_deleted` | `{ "id": <int> }` | After DELETE /api/tasks/<id> |
| `connected` | `{ "message": "..." }` | On client connect |

**Client usage:**
```javascript
const socket = io();
socket.on('task_updated', (data) => {
  console.log('Task changed:', data);
  refreshTaskList();
});
```

---

## Analytics Module

The `/api/analytics` endpoint uses Pandas and NumPy to compute:

```python
df = pd.DataFrame(tasks_list)
completed    = int(np.sum(df["status"] == "done"))
completion_pct = float(np.round((completed / len(df)) * 100, 2))
by_priority  = df["priority"].value_counts().to_dict()
daily_counts = df.groupby("date").size().tail(14)
```

---

## License

MIT — built for the Sankar Group Python Development Internship Assignment.
