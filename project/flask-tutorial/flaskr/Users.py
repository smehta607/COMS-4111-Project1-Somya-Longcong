# temp file, functions in this file will be addede to server.py
import functools
from sqlalchemy import *
from flask import Flask, request, render_template, g, redirect, Response, Blueprint, flash, flask_login
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from db import get_db

bp = Blueprint("Users", __name__, url_prefix="/Users")

engine = create_engine("postgresql://lx2305:lx23052175@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2")
conn = engine.connect()
cursor = conn.cursor()
# cursor.execute("SELECT * from Users")

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                cur.execute(
                    "INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)",
                    (username, username, generate_password_hash(password)),
                )
                db.commit()
            except Exception as e:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                print(e)
                error = f"Username {username} is already registered, try again!"
            else:
                # Success, go to the login page.
                flash("Thank you for registration!")
                return redirect(url_for("Users.login"))

        flash(error)

    return render_template("Users/register.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    flask_login.logout_user()
    return render_template('Home_page.html', message='Logged out', logout='yes')
