import os
# from sqlalchemy import *
# from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response



# def create_app(test_config=None):
# create and configure the app
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE = "postgresql://lx2305:lx23052175@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2",
)

# if test_config is None:
#     # load the instance config, if it exists, when not testing
#     app.config.from_pyfile('config.py', silent=True)
# else:
#     # load the test config if passed in
#     app.config.from_mapping(test_config)

# # ensure the instance folder exists
# try:
#     os.makedirs(app.instance_path)
# except OSError:
#     pass
# app.register_blueprint(Users.bp)

# if __name__ == "__main__":
#     import click

#     @click.command()
#     @click.option('--debug', is_flag=True)
#     @click.option('--threaded', is_flag=True)
#     @click.argument('HOST', default='0.0.0.0')
#     @click.argument('PORT', default=8111, type=int)
#     def run(debug, threaded, host, port):
#         HOST, PORT = host, port
#         print("running on %s:%d" % (HOST, PORT))
#         app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
#     run()

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello! Welcome to Work search process sharing platform!'

    return app