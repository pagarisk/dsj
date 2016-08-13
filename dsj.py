import os
import markdown
from flask import Flask, render_template, request, url_for, redirect, session, flash, abort, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import desc
from flask_wtf import Form
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, validators
from wtforms.fields.html5 import EmailField
from datetime import datetime, timedelta
import time

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'qwerty'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dsj.db'
db = SQLAlchemy(app)

# class definitions
class JobForm(Form):
    title = StringField('Title', [validators.Length(min = 3, max = 100)])
    location = StringField('Location', [validators.Length(min = 2, max = 100)])
    summary = TextAreaField('Job summary', [validators.Length(min = 1, max = 2000)])
    requirements = TextAreaField('Job requirements', [validators.Length(min = 1, max = 2000)])
    apply_info = TextAreaField('Application info', [validators.Length(min = 5, max = 500)])
    company = StringField('Company', [validators.Length(min = 1, max = 50)])
    company_link = StringField('Company website')
    about = TextAreaField('About company', [validators.Length(min = 1, max = 2000)])
    contact_email = StringField('Contact email', [validators.DataRequired(), validators.Email()])
    contact_name = StringField('Contact name')
    highlighted = BooleanField('Highlight listing')
    mailing_list = BooleanField('Include in newsletter')


class Job(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    create_date = db.Column(db.DateTime)
    publish_date = db.Column(db.DateTime)
    archive_date = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    extended = db.Column(db.Boolean)
    highlighted = db.Column(db.Boolean)
    mailing_list = db.Column(db.Boolean)
    title = db.Column(db.String(100))
    company = db.Column(db.String(100))
    location = db.Column(db.String(50))
    company_link = db.Column(db.String(200))
    summary = db.Column(db.String(2000))
    requirements = db.Column(db.String(2000))
    about = db.Column(db.String(2000))
    apply_info = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))
    contact_name = db.Column(db.String(120))

    def __init__(self, highlighted, mailing_list,
            title, company, location, company_link,
            summary, requirements, about, apply_info,
            contact_email, contact_name):
        if app.debug:
            self.status = 'Active'
        else:
            self.status = 'Review'
        self.highlighted = highlighted
        self.mailing_list = mailing_list
        self.create_date = datetime.now()
        self.publish_date = datetime.now() #+ datetime.timedelta(days = 2)
        if highlighted or mailing_list:
            self.extended = True
            self.archive_date = datetime.now() + timedelta(days = 60)
        else:
            self.extended = False
            self.archive_date = datetime.now() + timedelta(days = 30)
        self.title = title
        self.company = company
        self.location = location
        self.company_link = company_link
        self.summary = summary
        self.requirements = requirements
        self.about = about
        self.apply_info = apply_info
        self.contact_email = contact_email
        self.contact_name = contact_name

    def __repr__(self):
        return '<Job %r>' % self.id


# URL routings
@app.route('/')
def homepage():
    #jobs = None
    jobs = Job.query.filter_by(status = 'Active').order_by(desc(Job.id)).all()
    return render_template("home.html", jobs = jobs)


@app.route('/job/<int:id>')
def job(id):
    job = Job.query.filter_by(id = id).first_or_404()
    if job:
        return render_template("job.html", job = job)
    else:
        abort(404)

@app.route('/add')
def add_job():
    form = JobForm(request.form)
    return render_template("add.html", form = form)

@app.route('/preview', methods = ['POST'])
def preview_job():
    form = JobForm(request.form)
    job = Job(form.highlighted.data,
            form.mailing_list.data,
            form.title.data,
            form.company.data,
            form.location.data,
            form.company_link.data,
            form.summary.data,
            form.requirements.data,
            form.about.data,
            form.apply_info.data,
            form.contact_email.data,
            form.contact_name.data)
    job.summary = Markup(markdown.markdown(job.summary))
    job.requirements = Markup(markdown.markdown(job.requirements))
    job.about = Markup(markdown.markdown(job.about))
    session['job_summary_form'] = form.summary.data
    session['job_requirements_form'] = form.requirements.data
    session['job_about_form'] = form.about.data
    session['job_highlighted'] = job.highlighted
    session['job_mailing_list'] = job.mailing_list
    session['job_title'] = job.title
    session['job_company'] = job.company
    session['job_location'] = job.location
    session['job_company_link'] = job.company_link
    session['job_summary'] = job.summary
    session['job_requirements'] = job.requirements
    session['job_about'] = job.about
    session['job_apply_info'] = job.apply_info
    session['job_contact_email'] = job.contact_email
    session['job_contact_name'] = job.contact_name
    return render_template("preview.html", job = job)

@app.route('/submit', methods = ['POST'])
def submit_job():
    """
    form = JobForm(session['job_title'],
            session['job_location'],
            session['job_company'],
            session['job_summary'],
            session['job_requirements'],
            session['job_apply_info'],
            session['job_company'],
            session['job_company_link'],
            session['job_about'],
            session['job_contact_email'],
            session['job_contact_name'],
            session['job_highlighted'],
            session['job_mailing_list'])
    if form.validate():
    """
    new_job = Job(session['job_highlighted'],
                session['job_mailing_list'],
                session['job_title'],
                session['job_company'],
                session['job_location'],
                session['job_company_link'],
                session['job_summary'],
                session['job_requirements'],
                session['job_about'],
                session['job_apply_info'],
                session['job_contact_email'],
                session['job_contact_name'])
    new_job.summary = Markup(markdown.markdown(new_job.summary))
    new_job.requirements = Markup(markdown.markdown(new_job.requirements))
    new_job.about = Markup(markdown.markdown(new_job.about))
    db.session.add(new_job)
    db.session.commit()
    session.clear()
    flash('Thank you! Your job posting has been submitted.')
    if app.debug:
        return redirect(url_for('homepage'))
    else:
        return redirect(url_for('thank_you_page'))

@app.route('/thanks')
def thank_you_page():
    return render_template("thanks.html")

@app.route('/debug')
def debug():
    return session.get_cookie_path(app)

# admin section
admin = Admin(app, name = 'dsj', template_mode = 'bootstrap3')
admin.add_view(ModelView(Job, db.session))


# run only if the file is called directly
if __name__ == '__main__':
        app.run(host = '0.0.0.0')
