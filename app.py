from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_PATH = "todo.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

with app.app_context():
    init_db()

@app.route("/")
def index():
    filter_by = request.args.get("filter", "all")
    conn = get_db()
    if filter_by == "active":
        tasks = conn.execute("SELECT * FROM tasks WHERE done=0 ORDER BY created_at DESC").fetchall()
    elif filter_by == "done":
        tasks = conn.execute("SELECT * FROM tasks WHERE done=1 ORDER BY created_at DESC").fetchall()
    else:
        tasks = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE done=1").fetchone()[0]
    conn.close()
    return render_template("index.html", tasks=tasks, filter_by=filter_by,
                           total=total, done_count=done_count)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        conn = get_db()
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/toggle/<int:task_id>")
def toggle(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET done = 1 - done WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/clear_done")
def clear_done():
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE done=1")
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
