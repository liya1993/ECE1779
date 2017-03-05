from flask import Flask, request, render_template, redirect, url_for, flash
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

import mysql.connector

import tempfile
import os

from app import  webapp
# from wand.image import Image
import wand

photos = UploadSet('photos', IMAGES)
configure_uploads(webapp, photos)
patch_request_class(webapp)

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

@webapp.route('/user/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('login/login.html', form=form)

@webapp.route('/user/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('register/register.html', form=form)

@webapp.route('/user/trivial',methods=['GET'])
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

@webapp.route('/user/FileUpload/form',methods=['GET'])
#Return file upload form
def upload_form():
    return render_template("fileupload/form.html")

@webapp.route('/user/FileUpload', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        userid = request.form.get("userID")
        passowrd = request.form.get("password")

        # check if the post request has the file part
        if 'uploadedfile' not in request.files:
            # return "Missing uploaded file"
            flash(u'Missing uploaded file', 'info')

        file = request.files['uploadedfile']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # return 'Missing file name'
            flash(u'Missing file name', 'warning')

        if file:
            filename = photos.save(request.files['uploadedfile'])
            file_url = photos.url(filename)
            return render_template('base.html') + '<br><img src=' + file_url + '>'
    return render_template('base.html')

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
