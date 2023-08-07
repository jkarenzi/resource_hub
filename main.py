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
        query = request.args.get('query', "").lower()
        username = session.get('username')

        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )
        
        #retrieving posts and comments
        cursor = connection.cursor()
        sql_query = "SELECT id, title, user, content FROM posting ORDER BY id DESC"
        cursor.execute(sql_query)
        results = cursor.fetchall()
        sql_query1 = "SELECT post_id, id, user, comment FROM comments ORDER BY id DESC"
        cursor.execute(sql_query1)
        comments = cursor.fetchall()

        user_file = None
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    
        for file in uploaded_files:
            if file.startswith(username):
                user_file = file
                break

        if user_file is None:
            filename = 'person.png'
        else:
            filename = user_file    
        
        #handling search
        sql_query2 = "SELECT id, title, user, content FROM posting WHERE title LIKE %s OR content LIKE %s ORDER BY id DESC"
        query_1 = f'%{query}%'
        cursor.execute(sql_query2,(query_1, query_1))
        search_results = cursor.fetchall()
        connection.close()
    
        if search_results:
            return render_template('read_stats.html', uploaded_files=uploaded_files, results=search_results, comments=comments, filename=filename, username=session.get('username'))
        elif not search_results:
            message = "No matches found"
            return render_template('read_stats.html', message=message, uploaded_files=uploaded_files, results=search_results, comments=comments, filename=filename, username=session.get('username'))

        return render_template('read_stats.html', uploaded_files=uploaded_files, results=results, comments=comments, filename=filename, username=session.get('username'))
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
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
        
        #searching the uploaded_files list for a picture that corresponds with the current username
        user_file = None
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
            error_message = "Username already exists. Choose another one"
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
    session.pop('username', None)
    return redirect('/')


#this filter is used to make sure that if a user posts a link, then that link
#is displayed as a hyperlink, so that it will be clickable
@app.template_filter('autolink')
def autolink(s):
    #this regular expression matches links that may have been posted
    regex = r'https?://(?:[-\w]+\.)*(?:[-\w]+)\.(?:com|org|net|gov|edu|info|biz|co|io|dev)(?:/[-\w./?%&=]*)?'

    #here, we are replacing the original link with a clickable link
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


#this route gets the git template
@app.route('/git.html')
def get_git():
    filename = request.args.get('filename')
    return render_template('git.html', filename=filename, username=session.get('username'))


#this route gets the frontend template
@app.route('/frontend.html')
def get_frontend():
    filename = request.args.get('filename')
    return render_template('frontend.html', filename=filename, username=session.get('username'))


#this route handles user uploading profile picture
@app.route('/upload', methods=['POST'])
def upload():
    if 'username' in session:
        username = session.get('username')
        file = request.files['file']

        # Securing the filename(incase there are malicious xters)
        filename = secure_filename(file.filename)

        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
        for exist_file in uploaded_files:
            if exist_file.startswith(username):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], exist_file))
                break

        # Renaming the file with the username(naming convention to map usernames to their profile pics)
        filename1 = f"{username}_{filename}"

        # Saving the uploaded file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))

        return redirect('/form')
    return redirect('/')


#a filter to search for the right image based on the username prefix
@app.template_filter('find_user')
def find_user(uploaded_files, username):
    for item in uploaded_files:
        if item.startswith(username):
            return item
    return None


#route that redirects to form route
@app.route('/form.html')
def form_redirect():
    return redirect('/form')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)