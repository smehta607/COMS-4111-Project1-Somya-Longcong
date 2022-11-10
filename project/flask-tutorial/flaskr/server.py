#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
import flask
import flask_login
from flask import Flask, request, render_template, g, url_for, redirect, Response
from flask_wtf import FlaskForm
from flask import Flask, render_template, url_for, redirect, current_app
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import sqlite3

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
bcrypt = Bcrypt(app)


# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "lx2305"
DB_PASSWORD = "lx23052175"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://lx2305:lx23052175@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2"
db = SQLAlchemy(app)
# app.config['SECRET_KEY'] = DB_PASSWORD


# This line creates a database engine that knows how to connect to the URI above
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/index')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM Company")
  companyNames = []
  for result in cursor:
    companyNames.append(result['company_name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = companyNames)

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)


# This is an example of a different path.  You can see it at

#     localhost:8111/another

# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names


@app.route('/another')
def another():
  return render_template("anotherfile.html")

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def user_loader(user_id):
	return User.query.get(int(user_id))

class User(db.Model,flask_login.UserMixin):
  id = db.Column(db.String(80), primary_key=True)
  username = db.Column(db.String(20), nullable=False, unique=True)
  password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
  id = StringField(validators=[
    InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})
  username = StringField(validators=[
    InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
  password = PasswordField(validators=[
    InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

  submit = SubmitField('Register')

  def validate_username(self, username):
      existing_user_username = User.query.filter_by(username=username.data).first()
      if existing_user_username:
          raise ValidationError('That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
  email = StringField(validators=[
    InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})

  password = PasswordField(validators=[
    InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

  submit = SubmitField('Login')
  
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('profile'))
    return render_template('login.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('profile.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=True, threaded=threaded)


  run()
