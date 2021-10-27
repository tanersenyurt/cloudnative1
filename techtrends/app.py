import sqlite3
import logging
from datetime import datetime
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

total_db_count = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global total_db_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    total_db_count += 1
    return connection

def getTotalPostCount():
    connection = get_db_connection()
    posts = connection.execute('SELECT COUNT (*) FROM posts').fetchone()[0]
    connection.close()
    return posts

def get_date_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    app.logger.info(get_date_time_str()+', Home page retrieved!')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info(get_date_time_str()+', Article with id['+post_id+'] not found!')
      return render_template('404.html'), 404
    else:
      app.logger.info(get_date_time_str()+', Article '+post["title"]+' retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(get_timestamp_str() + ', "About Us" Page Retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
            app.logger.info(get_date_time_str()+', New article cannot created because title is empty!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(get_date_time_str()+', New article created with title "'+title+'""!')
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('healthz request successfull')
    return response

@app.route('/metrics')
def metrics():
    response = app.response_class(
            response=json.dumps({"db_connection_count": total_db_count , "post_count": getTotalPostCount()}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Metrics request successfull')
    return response

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(level=logging.DEBUG, filemode='w', format='%(levelname)s:%(name)s: %(message)s')
   app.run(host='0.0.0.0', port='3111')
