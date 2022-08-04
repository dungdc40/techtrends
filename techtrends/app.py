import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime
import time

# Function to get a database connection.
# This function connects to database with the name `database.db`
currentConnections = 0


def get_db_connection():
    global currentConnections
    currentConnections += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    currentConnections -= 1
    return connection


def write_log(message):
    timestamp = time.time()
    date_time = datetime.fromtimestamp(timestamp)
    str_date_time = date_time.strftime("%m/%d/%Y, %H:%M:%S")

    message = f"{str_date_time}, {message}"
    app.logger.info(message)

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        write_log(f"Article with id {post_id} does not exist")
        return render_template('404.html'), 404
    else:
        write_log(f"Article {post['title']} retrieved")
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    write_log(f"About us retrieved")
    return render_template('about.html')

# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            write_log(f"A new article with title {title} has been created")
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    write_log('Status request successfull')
    return response


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    row = connection.execute('SELECT COUNT(*) FROM posts').fetchone()

    response = app.response_class(
        response=json.dumps(
            {"db_connection_count": currentConnections, "post_count": row[0]}),
        status=200,
        mimetype='application/json'
    )

    write_log('Metrics request successfull')
    return response


# start the application on port 3111
if __name__ == "__main__":
    # Stream logs to a file, and set the default log level to DEBUG
    logging.basicConfig(filename='app.log', level=logging.DEBUG, force=True)
    app.run(host='0.0.0.0', port='3111')
