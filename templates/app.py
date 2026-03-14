from flask import Flask, render_template, request, redirect, url_for
# importing flask library to run our website

import sqlite3
# importing sqlite3 to use as our database

app = Flask(__name__)
# creating the flask app

DB_PATH = "todo.db"
# name of our database file

def get_db():
    # this function opens a connection to our database
    conn = sqlite3.connect(DB_PATH)
    # opens todo.db file
    conn.row_factory = sqlite3.Row
    # lets us read results like a dictionary
    return conn

def init_db():
    # this function creates the tasks table if it doesn't exist
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # id    = unique number for each task
    # title = the task text user types
    # done  = 0 means pending, 1 means completed
    # created_at = when the task was added
    conn.commit()
    # save the changes
    conn.close()
    # close the database connection

@app.route("/")
# when user opens localhost:5000, this function runs
def index():
    filter_by = request.args.get("filter", "all")
    # reads ?filter=active from the URL if present
    conn = get_db()

    if filter_by == "active":
        tasks = conn.execute("SELECT * FROM tasks WHERE done=0 ORDER BY created_at DESC").fetchall()
        # get only incomplete tasks
    elif filter_by == "done":
        tasks = conn.execute("SELECT * FROM tasks WHERE done=1 ORDER BY created_at DESC").fetchall()
        # get only completed tasks
    else:
        tasks = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
        # get all tasks

    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    # count total number of tasks

    done_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE done=1").fetchone()[0]
    # count how many tasks are completed

    conn.close()

    return render_template("index.html", tasks=tasks, filter_by=filter_by,
                           total=total, done_count=done_count)
    # send all data to index.html to display

@app.route("/add", methods=["POST"])
# runs when user submits the add task form
def add():
    title = request.form.get("title", "").strip()
    # reads the task text from the form
    if title:
        conn = get_db()
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        # inserts new task into database
        conn.commit()
        conn.close()
    return redirect(url_for("index"))
    # goes back to homepage

@app.route("/toggle/<int:task_id>")
# runs when user clicks the check button on a task
def toggle(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET done = 1 - done WHERE id=?", (task_id,))
    # if done=0 it becomes 1, if done=1 it becomes 0
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/delete/<int:task_id>")
# runs when user clicks the delete button on a task
def delete(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    # removes that task from database permanently
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/clear_done")
# runs when user clicks "Clear completed"
def clear_done():
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE done=1")
    # deletes all completed tasks at once
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    # creates the database table when app starts
    app.run(debug=True)
    # debug=True shows error details in browser during development
```

Press **Ctrl+S** to save.

---

### `requirements.txt`
```
flask==3.0.0
gunicorn==21.2.0
```

> `flask` — library to run our web app
> `gunicorn` — needed to deploy on Render

Press **Ctrl+S** to save.

---

### `.gitignore`
```
todo.db
__pycache__/
*.pyc
.env
venv/