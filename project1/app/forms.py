from flask import Flask, request, render_template, redirect, url_for, flash, g
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

import mysql.connector
from config import db_config

import tempfile
import os

from app import webapp
# from wand.image import Image
import wand

photos = UploadSet('photos', IMAGES)
configure_uploads(webapp, photos)
patch_request_class(webapp)

'''

Class Definitions

'''

class RegisterForm(FlaskForm):
    username = StringField(u'Username', validators=[
                DataRequired(message= u'Username can not be empty.'), Length(4, 16)])
    password = PasswordField('New Password', validators=[
        DataRequired(message= u'Password can not be empty.'),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField(u'Register')

class LoginForm(FlaskForm):
    username = StringField(u'Username', validators=[
               DataRequired(message=u'Username can not be empty.'), Length(4, 16)])
    password = PasswordField(u'Password',
                             validators=[DataRequired(message=u'Password can not be empty.')])
    submit = SubmitField(u'Login')

'''

Functions for Database

'''

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route('/user/trivial', methods=['GET'])
def trivial():
    cnx = mysql.connector.connect(user='root',
                                  password='8313947463',
                                  host='127.0.0.1',
                                  database='ECE1779')
    cursor = cnx.cursor()
    query = "SELECT * FROM courses"
    cursor.execute(query)
    view = render_template("trivial.html", title="Courses Table", cursor=cursor)
    cnx.close()
    return view

'''

Routers for Login

'''

@webapp.route('/user/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('login/login.html', form=form)

'''

Routers for Register

'''
@webapp.route('/user/register', methods=['GET', 'POST'])
# Display an empty HTML form that allows users to register a new account
# If everything in the form are right, save them in the dataabse to create a new account for the new user
def register():
    form = RegisterForm()
    username = request.form.get('username')
    password = request.form.get('password')
    if form.validate_on_submit():
        cnx = get_db()
        cursor = cnx.cursor()
        query = '''SELECT * FROM users WHERE login = %s'''
        cursor.execute(query, (username,))
        if cursor.fetchone() is not None:
            flash(u"That username is already taken.",'danger')
            return render_template('/register/register.html', form=form)
        else:
            query = ''' INSERT INTO users (login, password)
                               VALUES (%s,%s)
            '''
            cursor.execute(query, (username, password))
            cnx.commit()
            return redirect('/success')
    return render_template('register/register.html', form=form)

'''

Routers for Uploading Images

'''

@webapp.route('/user/FileUpload/form',methods=['GET'])
#Return file upload form
def upload_form():
    return render_template("fileupload/form.html")

@webapp.route('/user/FileUpload', methods=['GET','POST'])
#Show the uploaded image
def upload_file():
    if request.method == 'POST':
        userid = request.form.get("userID")
        passowrd = request.form.get("password")

        # check if the post request has the file part
        if 'uploadedfile' not in request.files:
            # return "Missing uploaded file"
            flash(u'Missing uploaded file', 'info')
            return render_template("fileupload/form.html")

        file = request.files['uploadedfile']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # return 'Missing file name'
            flash(u'Missing file name', 'warning')
            return render_template("fileupload/form.html")

        if file:
            filename = photos.save(request.files['uploadedfile'])
            file_url = photos.url(filename)
            return render_template('base.html') + '<br><img src=' + file_url + '>'
    return render_template('base.html')

'''

Routers for Transforming Images

'''

@webapp.route('/user/imagetransform/form',methods=['GET'])
#Return file upload form
def image_form():
    return render_template("imagetransform/form.html")

@webapp.route('/user/imagetransform',methods=['POST'])
#Upload a new image and tranform it
def image_transform():

    # check if the post request has the file part
    if 'image_file' not in request.files:
        return "Missing uploaded file"

    new_file = request.files['image_file']

    # if user does not select file, browser also
    # submit a empty part without filename
    if new_file.filename == '':
        return 'Missing file name'

    tempdir = tempfile.gettempdir()

    fname = os.path.join('app/static',new_file.filename)


    new_file.save(fname)

    img = Image(filename=fname)
    i = img.clone()
    i.rotate(90)

    fname_rotated = os.path.join('app/static', 'rotated_' + new_file.filename)

    i.save(filename=fname_rotated)

    return render_template("imagetransform/view.html",
                           f1=fname[4:],
                           f2=fname_rotated[4:])
