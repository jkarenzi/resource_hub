from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import pymysql
import re

app = Flask(__name__)
app.secret_key = 'kmj123456789'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

# this  route handles a get request for user posts


@app.route('/read_stats.html')
def get_data():
    if 'username' in session:
        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )

        cursor = connection.cursor()
        sql_query = "SELECT id, title, user, content FROM posting ORDER BY id DESC"
        cursor.execute(sql_query)
        results = cursor.fetchall()
        sql_query1 = "SELECT post_id, id, user, comment FROM comments ORDER BY id DESC"
        cursor.execute(sql_query1)
        comments = cursor.fetchall()
        connection.close()
        filename = request.args.get('filename')

        return render_template('read_stats.html', results=results, comments=comments, filename=filename, username=session.get('username'))
    return redirect('/')

# this route handles user posting


@app.route('/read_stats.html', methods=['POST'])
def get():
    title = request.form.get('title')
    content = request.form.get('content')
    user = session['username']

    connection = pymysql.connect(
        host='54.82.71.184',
        user='karenzi',
        password='@Karenzijoslyn46',
        database='posts'
    )

    cursor = connection.cursor()

    sql_query1 = "INSERT INTO posting (title, content, user) VALUES (%s, %s, %s)"
    cursor.execute(sql_query1, (title, content, user))
    connection.commit()
    connection.close()

    return redirect('/read_stats.html')


# this route returns the login form
@app.route('/')
def login():
    return render_template('login.html')


# this route handles user authentication
@app.route('/login', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    connection = pymysql.connect(
        host='54.82.71.184',
        user='karenzi',
        password='@Karenzijoslyn46',
        database='resourcehub_users'
    )

    cursor = connection.cursor()

    sql_query = "SELECT username, password FROM credentials"
    cursor.execute(sql_query)
    results = cursor.fetchall()
    connection.close()

    for row in results:
        user_name = row[0]
        pass_word = row[1]
        if user_name == username and check_password_hash(pass_word, password):
            session['username'] = username
            return redirect(f'/form?username={username}')

    error_message = "Invalid credentials"
    return render_template('login.html', error_message=error_message)


# this route returns the home page
@app.route('/form')
def form():
    if 'username' in session:
        username = session.get('username')

        # List all files in the 'uploads' folder. will return a list
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])

        #giving it a default value of None
        user_file = None

        #searching for a file that corresponds with our user
        for file in uploaded_files:
            if file.startswith(username):
                user_file = file
                break

        if user_file is None:
            return render_template('form.html', filename='person.png', username=username)
        return render_template('form.html', username=username, filename=user_file)
    return redirect('/')


# this route returns a signup page
@app.route('/signup.html')
def signup():
    return render_template('signup.html')


# this route adds new users to the database (signup)
@app.route('/signup', methods=['POST'])
def auth1():
    username = request.form.get('username')
    password = request.form.get('password')
    hashed_password = generate_password_hash(password)

    connection = pymysql.connect(
        host='54.82.71.184',
        user='karenzi',
        password='@Karenzijoslyn46',
        database='resourcehub_users'
    )

    cursor = connection.cursor()

    sql_query1 = "SELECT username FROM credentials"
    cursor.execute(sql_query1)
    results = cursor.fetchall()
    for name in results:
        if name[0] == username:
            error_message = "Username already exsits. Choose another one"
            return render_template('signup.html', error_message=error_message)

    sql_query = "INSERT INTO credentials (username, password) VALUES (%s, %s)"
    cursor.execute(sql_query, (username, hashed_password))
    connection.commit()
    connection.close()

    return redirect('/')


# this route handles deleting user posts
@app.route('/delete')
def delete():
    if 'username' in session:
        post_id = request.args.get('post_id', type=int)
        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )
        cursor = connection.cursor()

        sql_query = 'DELETE FROM posting WHERE id = %s'
        cursor.execute(sql_query, (post_id,))
        connection.commit()
        connection.close()

        return redirect('/read_stats.html')

    else:
        return redirect('/')


# this route logs out the user
@app.route('/logout')
def logout():
    # Clear the session
    session.pop('username', None)
    # Redirect to the login page
    return redirect('/')


# this filter is used to make sure that if a user posts a link, then that link
# is displayed as a hyperlink, so that it will be clickable
@app.template_filter('autolink')
def autolink(s):
    # Regular expression to find URLs in the string
    regex = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'

    # Replace URLs with clickable links
    return re.sub(regex, r'<a href="\g<0>" target="_blank">\g<0></a>', s)


@app.route('/add_comment', methods=['POST'])
def add_a_comment():
    post_id = int(request.form.get('post_id'))
    comment = request.form.get('comment')
    user = session['username']

    connection = pymysql.connect(
        host='54.82.71.184',
        user='karenzi',
        password='@Karenzijoslyn46',
        database='posts'
    )

    cursor = connection.cursor()

    sql_query = "INSERT INTO comments (post_id, comment, user) VALUES (%s, %s, %s)"
    cursor.execute(sql_query, (post_id, comment, user))
    connection.commit()
    connection.close()

    return redirect('/read_stats.html')

# this route gets the python.html template


@app.route('/python.html')
def get_python():
    filename = request.args.get('filename')
    return render_template('python.html', filename=filename, username=session.get('username'))

# this route gets the linux.html template


@app.route('/linux.html')
def get_linux():
    filename = request.args.get('filename')
    return render_template('linux.html', filename=filename, username=session.get('username'))


#this route handles user uploading profile picture


@app.route('/upload', methods=['POST'])
def upload():
    if 'username' in session:
        username = session.get('username')
        file = request.files['file']

        # Secure the filename
        filename = secure_filename(file.filename)

        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
        for existing_file in uploaded_files:
            if existing_file.startswith(username):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], existing_file))
                break

        # Rename the file with the username
        new_filename = f"{username}_{filename}"

        # Save the uploaded file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

        return redirect('/form')
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
