import os
import logging

import psycopg
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration is supplied through environment variables.
# Locally, Docker Compose will provide the PostgreSQL service hostname.
# In AWS, DB_HOST will be the RDS endpoint.

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tododb")
DB_USER = os.getenv("DB_USER", "todouser")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD environment variable must be set")


def get_db_connection():
    """Create a PostgreSQL database connection."""
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=5,
    )


def initialize_database():
    """Create the tasks table if it does not already exist."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )

    logger.info("Database initialized")


@app.errorhandler(psycopg.Error)
def handle_database_error(error):
    """Return a controlled response for database errors."""
    logger.exception("Database operation failed")
    return jsonify(error="Database operation failed"), 503


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CloudTasks</title>
    <style>
        :root {
            color-scheme: light;
            --ink: #172033;
            --muted: #64748b;
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --border: #e2e8f0;
            --surface: #ffffff;
            --background: #f5f7ff;
            --danger: #dc2626;
            --danger-hover: #b91c1c;
        }

        * {
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;
            margin: 0;
            padding: 48px 20px;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                         BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--ink);
            background:
                radial-gradient(ellipse at top left, #e0e7ff 0, transparent 42%),
                linear-gradient(135deg, #f8fafc, var(--background));
        }

        main {
            width: 100%;
            max-width: 720px;
            margin: 0 auto;
            padding: 36px;
            background: var(--surface);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 24px;
            box-shadow: 0 24px 70px rgba(30, 41, 59, 0.10);
        }

        h1 {
            margin: 0;
            font-size: clamp(2rem, 5vw, 2.6rem);
            letter-spacing: -0.045em;
            line-height: 1.15;
        }

        main > p:first-of-type {
            margin: 12px 0 28px;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.6;
        }

        form {
            display: flex;
            gap: 12px;
            margin-bottom: 18px;
        }

        input[type="text"] {
            flex: 1;
            min-width: 0;
            padding: 14px 16px;
            color: var(--ink);
            background: #fff;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            font: inherit;
            transition: border-color 160ms ease, box-shadow 160ms ease;
        }

        input[type="text"]::placeholder {
            color: #94a3b8;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.13);
        }

        button {
            padding: 12px 18px;
            border: 0;
            border-radius: 12px;
            background: var(--primary);
            color: #fff;
            font: inherit;
            font-weight: 650;
            cursor: pointer;
            transition: background 160ms ease, transform 160ms ease;
        }

        button:hover {
            background: var(--primary-hover);
        }

        button:active {
            transform: translateY(1px);
        }

        button:focus-visible,
        input[type="checkbox"]:focus-visible {
            outline: 3px solid rgba(79, 70, 229, 0.35);
            outline-offset: 3px;
        }

        #message {
            min-height: 24px;
            margin: 10px 0 24px;
            color: var(--muted);
            font-size: 0.92rem;
        }

        h2 {
            margin: 0 0 8px;
            font-size: 1.15rem;
            letter-spacing: -0.02em;
        }

        #tasks {
            margin: 0;
            padding: 0;
            list-style: none;
        }

        li {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 15px 0;
            border-bottom: 1px solid var(--border);
        }

        li:last-child {
            border-bottom: 0;
        }

        li span {
            flex: 1;
            min-width: 0;
            overflow-wrap: anywhere;
            line-height: 1.5;
        }

        li.done span {
            color: #94a3b8;
            text-decoration: line-through;
        }

        input[type="checkbox"] {
            width: 18px;
            height: 18px;
            flex: 0 0 auto;
            accent-color: var(--primary);
            cursor: pointer;
        }

        .delete {
            flex: 0 0 auto;
            padding: 8px 12px;
            background: #fff1f2;
            color: var(--danger);
            font-size: 0.88rem;
        }

        .delete:hover {
            background: #ffe4e6;
            color: var(--danger-hover);
        }

        @media (max-width: 540px) {
            body {
                padding: 24px 12px;
            }

            main {
                padding: 24px 18px;
                border-radius: 18px;
            }

            form {
                flex-direction: column;
            }

            form button {
                width: 100%;
            }

            li {
                gap: 10px;
            }

            .delete {
                padding: 8px 10px;
            }
        }
    </style>
</head>
<body>
<main>
    <h1>☁️ CloudTasks</h1>
    <p>A simple cloud-native task manager.</p>

    <form id="task-form">
        <input id="title" type="text" maxlength="200"
               placeholder="Enter an activity..." required>
        <button type="submit">Add</button>
    </form>

    <p id="message" role="status"></p>
    <h2>My activities</h2>
    <ul id="tasks"></ul>
</main>

<script>
async function api(path = "", options = {}) {
    const response = await fetch("/api/tasks" + path, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        }
    });

    if (!response.ok) {
        const result = await response.json().catch(() => ({}));
        throw new Error(result.error || "Request failed");
    }

    return response.json();
}

async function loadTasks() {
    const list = document.getElementById("tasks");
    const message = document.getElementById("message");

    try {
        const tasks = await api();
        list.replaceChildren();

        if (tasks.length === 0) {
            const item = document.createElement("li");
            item.textContent = "No activities yet. Add your first task!";
            list.appendChild(item);
            return;
        }

        tasks.forEach(task => {
            const item = document.createElement("li");
            item.className = task.completed ? "done" : "";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.checked = task.completed;
            checkbox.setAttribute("aria-label", "Mark completed");

            checkbox.addEventListener("change", async () => {
                try {
                    await api("/" + task.id, {
                        method: "PATCH",
                        body: JSON.stringify({
                            completed: checkbox.checked
                        })
                    });
                    await loadTasks();
                } catch (error) {
                    message.textContent = error.message;
                }
            });

            const title = document.createElement("span");
            title.textContent = task.title;

            const remove = document.createElement("button");
            remove.textContent = "Delete";
            remove.className = "delete";

            remove.addEventListener("click", async () => {
                try {
                    await api("/" + task.id, { method: "DELETE" });
                    await loadTasks();
                    message.textContent = "Task deleted.";
                } catch (error) {
                    message.textContent = error.message;
                }
            });

            item.append(checkbox, title, remove);
            list.appendChild(item);
        });
    } catch (error) {
        message.textContent = "Unable to load activities: " + error.message;
    }
}

document.getElementById("task-form").addEventListener("submit", async event => {
    event.preventDefault();

    const input = document.getElementById("title");
    const message = document.getElementById("message");
    const title = input.value.trim();

    if (!title) return;

    try {
        await api("", {
            method: "POST",
            body: JSON.stringify({ title })
        });

        input.value = "";
        message.textContent = "Activity added.";
        await loadTasks();
    } catch (error) {
        message.textContent = error.message;
    }
});

loadTasks();
</script>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(HTML)


@app.get("/health")
def health():
    """Check application and database connectivity."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")

        return jsonify(status="healthy", database="connected"), 200

    except psycopg.Error:
        logger.exception("Health check failed")
        return jsonify(status="unhealthy"), 503


@app.get("/api/tasks")
def list_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, completed, created_at
                FROM tasks
                ORDER BY id DESC
                """
            )
            rows = cur.fetchall()

    return jsonify([
        {
            "id": row[0],
            "title": row[1],
            "completed": row[2],
            "created_at": row[3].isoformat(),
        }
        for row in rows
    ])


@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify(error="A task title is required"), 400

    title = title.strip()

    if len(title) > 200:
        return jsonify(error="Maximum title length is 200 characters"), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (title)
                VALUES (%s)
                RETURNING id, title, completed, created_at
                """,
                (title,),
            )
            row = cur.fetchone()

    logger.info("Task created: %s", row[0])

    return jsonify({
        "id": row[0],
        "title": row[1],
        "completed": row[2],
        "created_at": row[3].isoformat(),
    }), 201


@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    completed = data.get("completed")

    if not isinstance(completed, bool):
        return jsonify(error="completed must be true or false"), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tasks
                SET completed = %s
                WHERE id = %s
                RETURNING id, title, completed, created_at
                """,
                (completed, task_id),
            )
            row = cur.fetchone()

    if row is None:
        return jsonify(error="Task not found"), 404

    return jsonify({
        "id": row[0],
        "title": row[1],
        "completed": row[2],
        "created_at": row[3].isoformat(),
    })


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id",
                (task_id,),
            )
            row = cur.fetchone()

    if row is None:
        return jsonify(error="Task not found"), 404

    return jsonify(message="Task deleted", id=row[0])


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000)
