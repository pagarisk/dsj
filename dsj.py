import os
import sqlite3
from flask import Flask, render_template, request, url_for, redirect, g, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import StringField, TextAreaField, IntegerField, validators
from datetime import datetime

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = '123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dsj.db'
db = SQLAlchemy(app)

# class definitions
class JobForm(Form):
    title = StringField('Title', [validators.Length(min = 3, max = 50)])
    company = StringField('Company', [validators.Length(min = 1, max = 50)])
    location = StringField('Location', [validators.Length(min = 2, max = 100)])
    applylink = StringField('Application link')
    companylink = StringField('Company website')
    summary = TextAreaField('Job summary', [validators.Length(min = 1, max = 2000)])
    requirements = TextAreaField('Job requirements', [validators.Length(min = 1, max = 2000)])
    about = TextAreaField('About company', [validators.Length(min = 1, max = 2000)])


class Job(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.String(50))
    date = db.Column(db.DateTime)
    title = db.Column(db.String(100))
    company = db.Column(db.String(100))
    location = db.Column(db.String(50))
    applylink = db.Column(db.String(200))
    companylink = db.Column(db.String(200))
    summary = db.Column(db.String(2000))
    requirements = db.Column(db.String(2000))
    about = db.Column(db.String(2000))

    def __init__(self, title, company, location,
            applylink, companylink, summary, requirements, about):
        self.status = 'Active'
        self.date = datetime.today().date()
        self.title = title
        self.company = company
        self.location = location
        self.applylink = applylink
        self.companylink = companylink
        self.summary = summary
        self.requirements = requirements
        self.about = about

    def __repr__(self):
        return '<Job %r>' % self.id


# URL routings
@app.route('/')
def homepage():
    return render_template("home.html")


@app.route('/job/<int:id>')
def job(id):
    job = Job.query.filter_by(id = id).first_or_404()
    if job:
        return render_template("job.html", job = job)
    else:
        abort(404)

@app.route('/form')
def form():
    return render_template("add.html")

@app.route('/add', methods = ['GET', 'POST'])
def add_job():
    form = JobForm(request.form)
    if request.method == 'POST' and form.validate():
        new_job = Job(form.title.data,
                form.company.data,
                form.location.data,
                form.applylink.data,
                form.companylink.data,
                form.summary.data,
                form.requirements.data,
                form.about.data)
        db.session.add(new_job)
        db.session.commit()
        flash('Thank you! Your job posting has been submitted.')
        return redirect(url_for('homepage'))
    return render_template("add.html", form = form)


# run only if the file is called directly
if __name__ == '__main__':
        app.run()
