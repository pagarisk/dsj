import os
import sqlite3
from flask import Flask, render_template, request, url_for, g, flash, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_object(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.path.join(app.root_path, 'dsj.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dsj.db'
db = SQLAlchemy(app)

"""
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'dsj.db'),
    SECRET_KEY = 'development key',
    USERNAME = 'admin',
    PASSWORD = 'admin'
))
"""
# app.config.from_envvar('DSJ_SETTINGS', silent = True)

# class definitions
class Job(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.String(50))
    date = db.Column(db.DateTime)
    title = db.Column(db.String(100))
    company = db.Column(db.String(100))
    location = db.Column(db.String(50))
    salary = db.Column(db.Integer)
    applylink = db.Column(db.String(200))
    companylink = db.Column(db.String(200))
    summary = db.Column(db.String(2000))
    requirements = db.Column(db.String(2000))
    about = db.Column(db.String(2000))

    def __init__(self, title, company, location, salary, \
            applylink, companylink, summary, requirements, about):
        self.status = 'Active'
        self.date = datetime.now()
        self.title = title
        self.company = company
        self.location = location
        self.salary = salary
        self.applylink = applylink
        self.companylink = companylink
        self.summary = summary
        self.requirements = requirements

    def __repr__(self):
        return '<Job %r>' % self.id




# DB functions
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# URL routings
@app.route('/')
def homepage():
    return render_template("home.html")


@app.route('/job/<int:id>')
def job(id):
    db = get_db()
    cur = db.execute('SELECT * FROM jobs WHERE id = %d' % id)
    job = cur.fetchone()
    if job:
        return render_template("job.html", job = job)
    else:
        abort(404)

@app.route('/form')
def form():
    return render_template("add.html")

@app.route('/add', methods = ['POST'])
def add_job():
    """
    db = get_db()
    db.execute('INSERT INTO jobs (status, title, summary, requirements, about, location, applylink, salary, company) values ("active", ?, ?, ?, ?, ?, ?, ?, ?)',
            [request.form['status'],
            request.form['title'],
            request.form['summary'],
            request.form['requirements'],
            request.form['about'],
            request.form['location'],
            request.form['applylink'],
            request.form['salary'],
            request.form['company']])
    db.commit()
    print (request.form)
    """
    new_job = Job(request.form['title'], \
            request.form['company'], \
            request.form['location'], \
            request.form['salary'], \
            request.form['applylink'], \
            request.form['companylink'], \
            request.form['summary'], \
            request.form['requirements'], \
            request.form['about'], \
            )
    flash('Thank you! Your posting has been submitted.')
    return redirect(url_for('home'))

# run only if the file is called directly
if __name__ == '__main__':
        app.run()
