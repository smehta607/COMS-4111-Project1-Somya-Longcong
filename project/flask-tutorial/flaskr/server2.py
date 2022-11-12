
import os
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
import flask
import flask_login
from flask import Flask, request, render_template, g, session, url_for, redirect, Response, flash, current_app
import datetime


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DB_USER = "lx2305"
DB_PASSWORD = "lx23052175"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"
engine = create_engine(DATABASEURI)
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  print(request.args)

  cursor = g.conn.execute("SELECT * FROM Company")
  d = {}
  for result in cursor:
    d[result['company_id']]= result['company_name']
  cursor.close()
  return render_template("index.html", d = d)

# class User(flask_login.UserMixin):
# pass

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        if not email or not name or not password:
            return "<a>Lack required information!</a><a href='/register'> Go back to registeration</a>"
        try:
            g.conn.execute("INSERT INTO Users (email, name, password) \
                        VALUES ('{0}', '{1}', '{2}')".format(email, name, password))
            print("Account Created!")
            return "<a>Account Created!</a><a href='/login'> Log in here</a>"
            g.conn.commit()
        except:
            cursor = g.conn.execute("select email from Users")
            for result in cursor:
                print(result)
            error = f"Email {email} is already registered, try again!"
            print(error)
            return "<a>Email is already registered, try again!!</a><a href='/register'>Back to register here</a>"
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        cursor = g.conn.execute("select * from Users where email = %s", (email,))
        user = cursor.fetchone()
        error = None
        if not user:
            error = "Incorrect email!"
            return "<a>Incorrect email!</a><a href='/login'> Log in again</a>"
        elif user["password"] != password:
            error = "Incorrect password!"
            return "<a>Incorrect password!</a><a href='/login'> Log in again</a>"
        if not error:
            session.clear()
            session['email'] = user['email']
            session['name'] = user['name']
            session['password'] = user['password']
            return flask.redirect(flask.url_for('profile'))
    return render_template("login.html")

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    try:
        name = session['name']
        email = session['email']
        return render_template("profile.html", name=name, email = email, message="Here's your profile")
    except:
        return "<a>You have not login!</a><a href='/login'> Log in here</a>"


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return "<a>Successfully Logout!</a><a href='/index'> Back to Home Page</a>"

@app.route('/following', methods=['GET', 'POST'])
def following():
    email = session['email']
    name = session['name']
    email_list = []
    cursor = g.conn.execute("select * from Followed where email_1 = %s", (email,))
    for result in cursor:
        email_list.append(result['email_2'])
    cursor.close()
    following = []
    for emails in email_list:
        cursor = g.conn.execute("select * from Users where email = %s", (emails,))
        following.append(cursor.fetchone()[1])
        cursor.close()
    return render_template("following.html", name=name, email = email, following = following)

@app.route('/follower', methods=['GET', 'POST'])
def follower():
    email = session['email']
    name = session['name']
    email_list = []
    cursor = g.conn.execute("select * from Followed where email_2 = %s", (email,))
    for result in cursor:
        email_list.append(result['email_1'])
    cursor.close()
    follower = []
    for emails in email_list:
        cursor = g.conn.execute("select * from Users where email = %s", (emails,))
        follower.append(cursor.fetchone()[1])
        cursor.close()
    return render_template("follower.html", name=name, email = email, follower = follower)

@app.route('/follow', methods = ['GET', 'POST'])
def follow():
    if request.method == "POST":
        try:
            myEmail = session['email']
            print("My email is " + myEmail)
        except:
            print("You have not login!")
            return "<a>You have not login!</a><a href='/login'> Log in here</a>"
        friendEmail = request.form['email']
        print("FriendEmail is " + friendEmail)
        if myEmail == friendEmail:
            print("You can not follow yourself!")
            return "<a>You can not follow yourself!</a><a href='/following'> Back to following</a>"
        email_list = []
        friendName = None
        cursor = g.conn.execute("select * from Users")
        for result in cursor:
            if result['email'] == friendEmail:
                friendName = result['name']
                print(friendName)
            email_list.append(result['email'])
        cursor.close()
        if friendEmail not in email_list or not friendName:
            print("Invalid email!")
            return "<a>Invalid email!</a> <a href='/following'> Back to following and find other one</a>"
        else:
            try:
                g.conn.execute("INSERT INTO Followed (email_1, email_2) VALUES ('{0}', '{1}')".format(myEmail, friendEmail))
                print("Successfully followed!")
                return "<a>Successfully followed %s!</a> <a href='/following'> Back to following</a>" % (friendName)
                g.conn.commit()
            except:
                return "<a> You have followed %s!</a><a href='/following'> Back to following and find other one</a>" % (friendName)
    return "<a>Successfully followed %s!</a> % (friendName) <a href='/following'> Back to following</a>"



@app.route('/<int:company_id>', methods=['GET', 'POST'])
def company(company_id):

    cursor = g.conn.execute("select company_name from Company where company_id = %s", company_id)
    companyName = ''
    for result in cursor:
        companyName = result['company_name']
    
    cursor = g.conn.execute("""select title, a.post_id from Added_Posts as a, belong_1 where 
        a.post_id = Belong_1.post_id and
        Belong_1.company_id =  %s""", company_id)
    titles = []
    for result in cursor:
        titles.append((result['title'],result['post_id'])) 
    context = dict(data = titles)
    return render_template("company.html", **context, companyName = companyName, company_id = company_id)

@app.route('/<int:company_id>/addpost', methods=['GET', 'POST'])
def addpost(company_id):
    if request.method == "POST":
        email = request.form['email']
        title = request.form['title']
        jobPosition = request.form['job_pos']
        jobLocation = request.form['job_loc']
        if not email or not title or not jobPosition or not jobLocation:
            return "<a>Lack required information!</a> <a href='/%s'> Back to company page</a>" % (company_id)
        myEmail = session['email']
        if myEmail != email:
            return "<a>Email Incorrect! Enter your login email!</a> <a href='/%s'> Back to company page</a>" % (company_id)
        cursor = g.conn.execute('SELECT max(post_id) max_post_id From Added_Posts')
        max_post_id = cursor.fetchone()['max_post_id']
        post_id = max_post_id + 1
        print(post_id)
        cursor.close()
        job_info = "Position: " + jobPosition+ "," + "Location: " +jobLocation
        print(job_info)
        try:
            g.conn.execute("INSERT INTO Added_Posts (post_id, email, title, job_info) \
                        VALUES ('{0}', '{1}', '{2}', '{3}')".format(post_id, email, title, job_info))
            g.conn.execute("INSERT INTO Belong_1 (company_id, post_id) \
                        VALUES ('{0}', '{1}')".format(company_id, post_id))
            print("Add new post!")
            return "<a>Add new post!</a><a href='/%s'> Back to company page</a>" % (company_id)
            g.conn.commit()
        except:
            cursor = g.conn.execute("select * from Added_Posts")
            for result in cursor:
                print(result)
            error = f"Email {email} is already registered, try again!"
            print(error)
            return "<a>Some errors, try again!!</a><a href='/%s'> Back to company page</a>" % (company_id)
    return company(company_id)

@app.route('/Posts')
def posts():
    name = session['name']

    cursor = g.conn.execute("""select title, post_id from Added_Posts, Users
    where Added_Posts.email = Users.email and
    Users.name = %s """, name)
    titles = []
    for result in cursor:
        titles.append((result['title'],result['post_id'])) 

    cursor.close()

    context = dict(data = titles)

    return render_template("Posts.html", **context, name=name)

@app.route('/Posts/<int:post_id>')
def individual_post(post_id):
    cursor = g.conn.execute("""select title from Added_Posts
        where post_id = %s""", post_id) 
    titles = []
    for result in cursor:
        titles.append(result['title'])  # can also be accessed using result[0]

    desc=[]
    cursor = g.conn.execute("""select description, timestamps from Belong_2_Events
        where post_id = %s""", post_id)
    for result in cursor:
        desc.append((result["description"], result["timestamps"]))

    coms = []
    cursor = g.conn.execute(""" select content from Comments_Attached 
        where post_id = %s""", post_id)
    for result in cursor:
        coms.append(result['content'])
    
    cursor = g.conn.execute("""select name from Users, Added_Posts
        where post_id = %s and
        Added_Posts.email = Users.email""", post_id)
    name = ""
    for result in cursor:
        name = result['name']
    cursor.close()


    context = dict(data = desc, t = titles, c=coms)
    return render_template("single_post.html", **context, name=name, post_id= post_id)


@app.route('/<int:post_id>/addevent', methods=['GET', 'POST'])
def addevent(post_id):
    if request.method == "POST":
        pid = post_id
        desc = request.form['desc']
        timestamp = datetime.datetime.now()
        print(timestamp)
        if not pid or not desc:
            return "<a>Lack required information!</a> <a href='/%s'> Back to Post page</a>" % (post_id)
        
        cursor = g.conn.execute('SELECT max(events_id) max_events_id From Belong_2_Events')
        max_events_id = cursor.fetchone()['max_events_id']
        events_id = max_events_id + 1
        print(events_id)
        cursor.close()
        try:
            g.conn.execute("INSERT INTO Belong_2_Events (events_id, post_id, description, timestamps) \
                        VALUES ('{0}', '{1}', '{2}', '{3}')".format(events_id, post_id, desc, timestamp))
            print("Added new event!")
            return "<a>Added new event!</a><a href='/Posts/%s'> Back to post page</a>" % (post_id)
            g.conn.commit()
        except:
            cursor = g.conn.execute("select * from Belong_2_Events")
            for result in cursor:
                print(result)
            return "<a>Some errors, try again!!</a><a href='/Posts/%s'> Back to post page</a>" % (post_id)
    return post(post_id)

@app.route('/<int:post_id>/addcomment', methods=['GET', 'POST'])
def addcomment(post_id):
    if request.method == "POST":
        pid = post_id
        content = request.form['cont']
        if not pid or not content:
            return "<a>Lack required information!</a> <a href='/%s'> Back to Post page</a>" % (post_id)
        
        cursor = g.conn.execute('SELECT max(comment_id) max_comment_id From Comments_Attached')
        max_comment_id = cursor.fetchone()['max_comment_id']
        comment_id = max_comment_id + 1
        print(comment_id)
        cursor.close()
        try:
            g.conn.execute("INSERT INTO Comments_Attached (comment_id, content, post_id) \
                        VALUES ('{0}', '{1}', '{2}')".format(comment_id, content, pid))
            print("Added new comment!")
            return "<a>Added a new comment!</a><a href='/Posts/%s'> Back to post page</a>" % (post_id)
            g.conn.commit()
        except:
            cursor = g.conn.execute("select * from Comments_Attached")
            return "<a>Some errors, try again!!</a><a href='/Posts/%s'> Back to post page</a>" % (post_id)
    return post(post_id)
if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=True, threaded=threaded)

  run()

