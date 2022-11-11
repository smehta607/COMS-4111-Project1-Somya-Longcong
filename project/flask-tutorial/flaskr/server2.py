
import os
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
import flask
import flask_login
from flask import Flask, request, render_template, g, session, url_for, redirect, Response, flash, current_app


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

@app.route('/index')
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
  companyNames = []
  for result in cursor:
    companyNames.append(result['company_name'])
  cursor.close()
  context = dict(data = companyNames)
  return render_template("index.html", **context)

# class User(flask_login.UserMixin):
# 	pass

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
            # print("Lack required information!")
            # return flask.redirect(flask.url_for('register'))
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
            return "<a>Invalid email!</a><a> href='/following'> Back to following and find other one</a>"
        else:
            try:
                g.conn.execute("INSERT INTO Followed (email_1, email_2) VALUES ('{0}', '{1}')".format(myEmail, friendEmail))
                print("Successfully followed!")
                return "<a>Successfully followed %s!</a> <a href='/following'> Back to following</a>" % (friendName)
                g.conn.commit()
            except:
                return "<a> You have followed %s!</a><a href='/following'> Back to following and find other one</a>" % (friendName)
    return "<a>Successfully followed %s!</a> % (friendName) <a href='/following'> Back to following</a>"


@app.route('/others_profile', methods=['GET', 'POST'])
def others_profile(email):
    return render_template("others_profile")

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

