<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

POSTS_FILE = "post.json"

# ------------------------------
# Helpers
# ------------------------------
def load_posts():
    if not os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "w") as file:
            f.write("[]")
    with open(POSTS_FILE, "r") as file:
        return json.load(file)

def save_posts(posts):
    with open(POSTS_FILE, "w") as file:
        json.dump(posts, file, indent=4)

def fetch_post_by_id(post_id):
    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            return post
    return None

# connecting to database
def load_testimonies(post_id):
    conn = sqlite3.connect("DB/testimonies.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM testimonies WHERE post_id = ?",
        (post_id,)
    )

    testimonies = cursor.fetchall()
    conn.close()

    return testimonies

# ------------------------------
# Simple Login
# ------------------------------
USER = {"username": "admin", "password": "1234"}

# ------------------------------
# Routes
# ------------------------------

@app.route('/')
def home():
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        posts = load_posts()
        new_post = {
            "id": max([p['id'] for p in posts], default=0) + 1,
            "title": request.form.get('title'),
            "author": request.form.get('author'),
            "content": request.form.get('content'),
            "likes": 0
        }
        posts.append(new_post)
        save_posts(posts)
        return redirect(url_for('home'))

    return render_template('add.html')

@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    posts = load_posts()
    post = fetch_post_by_id(post_id)

    if request.method == 'POST':
        post['title'] = request.form.get('title')
        post['author'] = request.form.get('author')
        post['content'] = request.form.get('content')
        save_posts(posts)
        return redirect(url_for('home'))

    return render_template('update.html', post=post)

@app.route('/delete/<int:post_id>')
def delete(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    posts = load_posts()
    posts = [p for p in posts if p['id'] != post_id]
    save_posts(posts)
    return redirect(url_for('home'))

@app.route('/like/<int:post_id>')
def like(post_id):
    posts = load_posts()
    post = fetch_post_by_id(post_id)
    if post:
        post['likes'] += 1
        save_posts(posts)
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USER["username"] and request.form['password'] == USER["password"]:
            session['user'] = request.form['username']
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/testimonies/<int:post_id>')
def testimonies(post_id):
    post = fetch_post_by_id(post_id)
    testimonies = load_testimonies(post_id)

    return render_template(
        'testimonies.html',
        post=post,
        testimonies=testimonies
    )



# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
=======
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
>>>>>>> aac4f8e7fe974afb85025ab8b4e42cf3ec22268a
