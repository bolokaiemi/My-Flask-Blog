from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash  # For hashed passwords
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
from werkzeug.security import generate_password_hash
import json
import os
import sqlite3

app.secret_key = "secret123"

POSTS_FILE = "post.json"
REVIEW_FILE = "reviews.json"

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


def load_reviews():
    if not os.path.exists(REVIEW_FILE):
        return []
    with open(REVIEW_FILE, "r") as f:
        return json.load(f)


def save_reviews(reviews):
    with open(REVIEW_FILE, "w") as f:
        json.dump(reviews, f, indent=4)

# ------------------------------
# Simple Login
# ------------------------------
#USER = {"username": "Ebi", "password": "Vien2347"}


class User(db.Model):
    __tablename__ = 'users'  # explicit table name (cleaner)

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    username = db.Column(db.String(120), unique=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

# ------------------------------
# Routes
# ------------------------------

# Home route
# ----------------------------
@app.route('/')
def home():
    posts = load_posts()

    return render_template('index.html', posts=posts)


# Add route
# ----------------------------
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

# Update route
# ----------------------------
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

        form.title.data = post.title
        form.content.data = post.content

    return render_template('update.html', post=post, post_id=post_id)

# Delete route
# ----------------------------
@app.route('/delete/<int:post_id>', methods=['GET', 'POST'])
def delete(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    posts = load_posts()
    post = fetch_post_by_id(posts,post_id)

    if not post:
        return "Post not found", 404

    # POST = delete
    if request.method == 'POST':
        posts = [post for post in posts if post["id"] != post_id]
        save_posts(posts)
        return redirect(url_for('home'))

    # GET = show confirmation page
    return render_template('delete.html', post=post)



# Like route
# ----------------------------
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
            save_posts(posts)
            return redirect(url_for('home'))

# Login route
# ----------------------------

from flask import request, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user'] = user.username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', message="Invalid username or password")

    return render_template('login.html')


# Logout route
# ----------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


# testimonies route
# ----------------------------
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


with app.app_context():
    db.create_all()
# Signup page (GET)
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('sign-up.html')

# Signup form handler (POST)
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Password validation
    if len(password) < 6:
        return render_template('sign-up.html', message='Password must be at least 6 characters')

    # Check if username exists
    if User.query.filter_by(username=username).first():
        return render_template('sign-up.html', message='Username already taken')

    # Check if email exists
    if User.query.filter_by(email=email).first():
        return render_template('sign-up.html', message='Email already registered')

    # Hash password
    hashed_password = generate_password_hash(password)

    # Save user
    new_user = User(
        name=name,
        username=username,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('home'))
    #return render_template('sign-up.html', message='✅ Signup successful!')


# ----------------------------
# Review route
# ----------------------------

@app.route('/review', methods=['GET', 'POST'])
def review():
    reviews = load_reviews()
    message = ""

    if request.method == 'POST':
        post_id = request.form.get('post_id')
        post = fetch_post_by_id(post_id)
        # 🚨 check if post exists
        if not post:
            return "Post not found"

        name = request.form.get('name')
        review_text = request.form.get('review')

        new_review = {
            "post_id": post_id,
            "name": name,
            "review": review_text
        }

        reviews.append(new_review)
        save_reviews(reviews)

        message = "✅ Review submitted successfully!"

    return render_template(
        'review.html',
        reviews=reviews,
        message=message
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

