from flask import Flask, flash, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
import os
import pymysql
import re

app = Flask(__name__)
app.secret_key = 'kmj123456789'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.permanent_session_lifetime = timedelta(minutes=30)


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

    sql_query = "SELECT username, password, admin FROM credentials"
    cursor.execute(sql_query)
    results = cursor.fetchall()
    connection.close()

    for row in results:
        user_name = row[0]
        pass_word = row[1]
        admin_status = row[2]
        if user_name == username and check_password_hash(pass_word, password):
            session.permanent = True
            session['username'] = username
            session['admin_status'] = admin_status
            flash("Login successful", "login")
            return redirect('/form')

    error_message = "Invalid credentials"
    return render_template('login.html', error_message=error_message)


# this route returns the home page
@app.route('/form')
def form():
    if 'username' in session:
        username = session.get('username')
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
        admin_status = session.get('admin_status')
        
        #searching the uploaded_files list for a picture that corresponds with the current username
        user_file = None
        for file in uploaded_files:
            if file.startswith(username):
                user_file = file
                break

        if user_file is None:
            return render_template('form.html', filename='person.png', username=username, admin_status=admin_status)
        return render_template('form.html', username=username, filename=user_file, admin_status=admin_status)
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
    flash("Signup successful", "signup")
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
    session.clear()
    flash("You've been logged out", "logout")
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
    if 'username' in session:
        filename = request.args.get('filename')
        
        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )

        cursor = connection.cursor()

        sql_query = "SELECT * FROM resources WHERE topic = %s ORDER BY avg_rating DESC, id DESC"
        topic_name = 'python'
        cursor.execute(sql_query,(topic_name,))
        resource_list = cursor.fetchall()
        connection.close()

        return render_template('python.html', filename=filename, admin_status=session.get('admin_status'), resource_list=resource_list, username=session.get('username'))
    return redirect('/')

# this route gets the linux.html template
@app.route('/linux.html')
def get_linux():
    if 'username' in session:
        filename = request.args.get('filename')
        
        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )

        cursor = connection.cursor()

        sql_query = "SELECT * FROM resources WHERE topic = %s ORDER BY avg_rating DESC, id DESC"
        topic_name = 'shell scripting'
        cursor.execute(sql_query,(topic_name,))
        resource_list = cursor.fetchall()
        connection.close()

        return render_template('linux.html', filename=filename, admin_status=session.get('admin_status'), resource_list=resource_list, username=session.get('username'))
    return redirect('/')

#this route gets the git template
@app.route('/git.html')
def get_git():
    if 'username' in session:
        filename = request.args.get('filename')
        
        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )

        cursor = connection.cursor()

        sql_query = "SELECT * FROM resources WHERE topic = %s ORDER BY avg_rating DESC, id DESC"
        topic_name = 'git'
        cursor.execute(sql_query,(topic_name,))
        resource_list = cursor.fetchall()
        connection.close()

        return render_template('git.html', filename=filename, admin_status=session.get('admin_status'), resource_list=resource_list, username=session.get('username'))
    return redirect('/')

#this route gets the frontend template
@app.route('/frontend.html')
def get_frontend():
    if 'username' in session:
        filename = request.args.get('filename')
        
        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )

        cursor = connection.cursor()

        sql_query = "SELECT * FROM resources WHERE topic = %s ORDER BY avg_rating DESC, id DESC"
        topic_name = 'frontend development'
        cursor.execute(sql_query,(topic_name,))
        resource_list = cursor.fetchall()
        connection.close()

        return render_template('frontend.html', filename=filename, admin_status=session.get('admin_status'), resource_list=resource_list, username=session.get('username'))
    return redirect('/')

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


#route that gets admin.html page
@app.route('/admin.html')
def get_admin():
    if 'username' not in session:
        return redirect('/')
    
    if session['admin_status']:
        user = session.get('username')
        user_file = None
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])

        for file in uploaded_files:
            if file.startswith(user):
                user_file = file
                break

        if user_file is None:
            filename = 'person.png'
        else:
            filename = user_file  

        topic = request.args.get("topic_feedback", "")
        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )

        cursor = connection.cursor()

        sql_query = 'SELECT * FROM ratings WHERE topic = %s'
        cursor.execute(sql_query, (topic,))
        rating_results = cursor.fetchall()

        if not rating_results and topic:
            error = "No feedback available"
            return render_template('admin.html', filename=filename, username = session.get('username'), rating_results=rating_results, error=error)

        return render_template('admin.html', filename=filename, username = session.get('username'), rating_results=rating_results)
    error_message = 'Unauthorized access. Please login with an admin account to access this route'
    return render_template('no_access.html', error_message=error_message)


#route that handles posting of resources
@app.route('/admin', methods=['POST'])
def add_resource():
    user = session.get('username')
    topic = request.form.get('topic')
    title = request.form.get('title')
    description = request.form.get('description')
    the_link = request.form.get('the_link')

    connection = pymysql.connect(
        host='54.82.71.184',
        user='karenzi',
        password='@Karenzijoslyn46',
        database='posts'
    )

    cursor = connection.cursor()

    sql_query = "INSERT INTO resources (user, topic, title, description, the_link) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql_query, (user, topic, title, description, the_link))
    connection.commit()
    connection.close()
    flash("Resource successfully added", "add")

    return redirect('/admin.html')


#route that handles deleting resources
@app.route('/delete_resource')
def del_resource():
    if 'username' in session and session['admin_status']:
        resource_id = request.args.get('resource_id', type=int)

        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )
        cursor = connection.cursor()

        sql_query = 'DELETE FROM resources WHERE id = %s'
        cursor.execute(sql_query, (resource_id,))
        connection.commit()
        connection.close()
        flash("Resource successfully deleted", "delete")

        return redirect('/form')

    else:
        error_message = 'Unauthorized access. Please login with an admin account to access this route'
        return render_template('no_access.html', error_message=error_message)


#this route calculates avg rating and stores it in db
@app.route('/rating', methods=['POST'])
def rating():
    if 'username' in session:
        rating = int(request.form.get('rating'))
        resource_id = int(request.form.get('resource_id'))
        user = request.form.get('user')
        feedback = request.form.get('optional_feed')
        topic = request.form.get('topic')
        title = request.form.get('title')

        connection = pymysql.connect(
            host='54.82.71.184',
            user='karenzi',
            password='@Karenzijoslyn46',
            database='posts'
        )

        cursor = connection.cursor()

        sql_query3 = 'SELECT user FROM ratings WHERE resource_id = %s'
        cursor.execute(sql_query3, (resource_id,))
        user_list = cursor.fetchall()
        for name in user_list:
            if name[0] == user:
                flash("You've rated this resource before", "rate1")
                return redirect('/form')
        if feedback:
            sql_query = 'INSERT INTO ratings (resource_id, user, rating, description, topic, title) VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(sql_query, (resource_id, user, rating, feedback, topic, title))
            connection.commit()
        else:
            sql_query = 'INSERT INTO ratings (resource_id, user, rating, topic) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(sql_query, (resource_id, user, rating, topic, title))
            connection.commit()


        sql_query1 = 'SELECT rating FROM ratings WHERE resource_id = %s'
        cursor.execute(sql_query1, (resource_id,))
        rating_list = cursor.fetchall()
        sum = 0
        total_ratings = len(rating_list)
        for num in rating_list:
            num = int(num[0])
            sum += num
        avg_rating = round(sum / total_ratings, 1)

        sql_query2 = 'UPDATE resources SET avg_rating = %s WHERE id = %s'
        cursor.execute(sql_query2, (avg_rating, resource_id))
        connection.commit()

        connection.close()
        flash("Thank you! your feedback is valued", "rate")
        return redirect('/form')
    
    return redirect('/')    


#this route handles granting of admin privileges
@app.route('/add_admin', methods=['POST'])
def add_admin():
    admin_account = request.form.get('admin_account')

    connection = pymysql.connect(
        host='54.82.71.184',
        user='karenzi',
        password='@Karenzijoslyn46',
        database='resourcehub_users'
    )

    cursor = connection.cursor()

    sql_query = "SELECT username, admin FROM credentials"
    cursor.execute(sql_query)
    all_accounts = cursor.fetchall()

    for row in all_accounts:
        if admin_account in row:
            if row[1]:
                flash("&#9888; Account already admin", 'admin')
                return redirect('/admin.html')
            else:
                sql_query1 = "UPDATE credentials SET admin = %s WHERE username = %s"  
                value = 1
                cursor.execute(sql_query1, (value, admin_account))
                connection.commit()
                connection.close()
                flash("Account type changed to admin", 'admin1') 
                return redirect('/admin.html')
        else:
            pass   
    flash("&#9888; Account doesn't exist", "admin")
    return redirect('/admin.html')     

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)