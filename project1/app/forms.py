# from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash
# from app import webapp
# from werkzeug.utils import secure_filename
#
# import tempfile
# import os
#
# ALLOWED_EXTENSIONS= set(['png','jpg','gif','jpeg'])
# webapp.config['UPLOAD_FOLDER']=os.getcwd()
# webapp.config['MAX_CONTENT_LENGTH']= 16*1024*1024
#
# def allowed_file(filename):
#     return '.' in filename and \
#     filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
#
# @webapp.route('/user/FileUpload/<filename>')
# def showimage(filename):
#     return send_from_directory(webapp.config['UPLOAD_FOLDER'],
#                                filename)
#
# @webapp.route('/user/FileUpload/form',methods=['GET'])
# #Return file upload form
# def upload_form():
#     return render_template("form.html")
#
#
# @webapp.route('/user/FileUpload',methods=['POST'])
# #Upload a new file and store in the systems temp directory
# def file_upload():
#     userid = request.form.get("userID")
#     passowrd = request.form.get("password")
#
#     # check if the post request has the file part
#     if 'uploadedfile' not in request.files:
#         # return "Missing uploaded file"
#         flash(u'Missing uploaded file','info')
#
#     new_file = request.files['uploadedfile']
#
#     # if user does not select file, browser also
#     # submit a empty part without filename
#     if new_file.filename == '':
#         # return 'Missing file name'
#         flash(u'Missing file name','warning')
#
#     if new_file and allowed_file(new_file.filename):
#         filename = secure_filename(new_file.filename)
#         new_file.save(os.path.join(webapp.config['UPLOAD_FOLDER'], filename))
#         file_url = url_for('showimage', filename=filename)
#         return render_template('base.html') + '<br><img src=' + file_url + '>'
#     return render_template('base.html')
#     # tempdir = tempfile.gettempdir()
#
#     # new_file.save(os.path.join(tempdir,new_file.filename))
#
#     # return "Sucess"

# try to use flask_uploads to solve image upload problem

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email

from app import webapp


photos = UploadSet('photos', IMAGES)
configure_uploads(webapp, photos)
patch_request_class(webapp)

class RegisterForm(FlaskForm):
    email = StringField(u'Email', validators=[
                DataRequired(message= u'Email can not be empty.'), Length(1, 64),
                Email(message= u'Please type in a valid email address，such as：username@domain.com.')])
    password = PasswordField(u'Password',
                  validators=[DataRequired(message= u'Password can not be empty.')])
    submit = SubmitField(u'Register')

@webapp.route('/user/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    # if form.validate_on_submit():
    return render_template('register.html', form=form)

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
