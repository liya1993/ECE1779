from app import webapp
from flask import render_template

@webapp.route('/',methods=['GET'])
#Return html with pointers to the examples
def main():
    return render_template("main.html")