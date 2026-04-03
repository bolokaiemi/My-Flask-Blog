from fileinput import filename

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
            file.write("[]")
    with open(POSTS_FILE, "r") as file:
        return json.load(file)

def save_posts(posts):
    with open(POSTS_FILE, "w") as file:
        json.dump(posts, file, indent=4)

def fetch_post_by_id(posts, post_id):
    for post in posts:
        if post['id'] == post_id:
            return post
    return None


def load_testimonies(post_id):
    conn = sqlite3.connect("testimonies.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, content FROM testimonies WHERE post_id = ?",
        (post_id,)
    )

    data = cursor.fetchall()
    conn.close()

    return data



# ------------------------------
# Simple Login
# ------------------------------
USER = {"username": "Ebi", "password": "Vien2347"}

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
    post_id = post_id
    posts = load_posts()
    post = fetch_post_by_id(posts, post_id,)

    if request.method == 'POST':
        post['title'] = request.form.get('title')
        post['author'] = request.form.get('author')
        post['content'] = request.form.get('content')
        save_posts(posts)
        return redirect('/')

    return render_template('update.html', post=post, post_id=post_id)

@app.route('/delete/<int:post_id>', methods=["post"])
def delete(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    posts = load_posts()
    posts = [post for post in posts if post['id'] != post_id]
    save_posts(posts)
    return redirect(url_for('home'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like(post_id):
    # check login
    if 'user' not in session:
        return redirect(url_for('signup'))

    posts = load_posts()
    posts = load_posts()

    for post in posts:
        if post['id'] == post_id:

            # ✅ ensure likes exists FIRST
            if 'likes' not in post:
                post['likes'] = 0

            # ✅ then increment
            post['likes'] += 1

            print("LIKE UPDATED:", post['likes'])
            break

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
def testimonies( post_id):
    posts = load_posts()
    post = fetch_post_by_id(posts, post_id)

    # 🚨 check if post exists
    if not post:
        return "Post not found"

    testimonies = []

    try:
        testimonies = load_testimonies(post_id)
    except Exception as e:
        print("DB ERROR:", e)

    return render_template(
        'testimonies.html',
        post=post,
        testimonies=testimonies
    )



@app.route('/submit_testimony', methods=['POST'])
def submit_testimony():
    post_id = request.form.get('post_id')
    content = request.form.get('content')

    # 🚨 basic validation
    if not content:
        return "Testimony cannot be empty"

    conn = sqlite3.connect("testimonies.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO testimonies (post_id, content) VALUES (?, ?)",
        (post_id, content)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('testimonies', post_id=post_id))


@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    if len(password) < 6:
        return render_template('sign-up.html', message='Password must be at least 6 characters')

    # Here you would normally save to a database
    print(name, email, password)

    return render_template('sign-up.html', message=f'Welcome {name}, signup successful!')




# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

