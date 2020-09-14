import os
import secrets
import requests
import json
from datetime import datetime
from flask import render_template, url_for, request, jsonify, flash, redirect, request, abort
from flask_json import json_response
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, SentenceForm
from app.models import User, Sentence
from flask_login import login_user, current_user, logout_user, login_required



@app.route('/')
@app.route('/home')
def home(): 
    return render_template('home.html')

@app.route('/questions')
def questions():
    sentences = Sentence.query.all()
    return render_template('questions.html',sentences = sentences)

@app.route('/form')
def my_form():
    return render_template('form.html')
    #  return redirect(url_for('my_form_get'))

@app.route('/form', methods = ['GET','POST'])
def my_form_get():

    text = request.form.get('text') 
    posts = requests.post('http://35.192.90.7/predict', data=text.encode('utf-8'))
    posts = posts.json()
    return render_template('demoQuestions.html',posts=posts,text=text)

# @app.route("/json", methods=['POST','GET'])
# def json():
 
#     req_data = request.get_json()
#     entity1 = req_data['e1']
#     entity2 = req_data['e2']
#     relation = req_data['relation']
#     sentence = req_data['sentence']
    
#     for index in range(len(req_data)):
#         for key in req_data[index]:
#             print(req_data['index'][0]['key'])

    
# @app.route('/get_time')
# def get_time():
#     now = datetime.utcnow()
#     return json_response(time=now)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect (url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account created has been created! You are now able to log in', 'success')
        return redirect(url_for('questions'))
    return render_template('register.html', title = 'Register', form = form)

@app.route("/login",methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect (url_for('questions'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect (next_page) if next_page else redirect(url_for('questions'))
        else:
            flash('Login Unsuccessful. Please check username and password','danger')
    return render_template('login.html', title = 'Login', form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics',picture_fn)
    form_picture.save(picture_path)

    return picture_fn

@app.route("/account",methods = ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title = 'Account', image_file=image_file, form=form)


@app.route("/question/new",methods = ['GET', 'POST'])
@login_required
def new_question():
    form = SentenceForm()
    if form.validate_on_submit():
        sentence = Sentence(question=form.question.data, answer=form.answer.data, author = current_user)
        db.session.add(sentence)
        db.session.commit()
        flash('Your question has been created!', 'success')
        return redirect(url_for('questions'))
    return render_template('create_question.html', title = 'New Question', form = form, legend = 'New Question')

@app.route("/sentence/<int:sentence_id>")
def sentence(sentence_id):
    sentence = Sentence .query.get_or_404(sentence_id)
    return render_template('sentence.html',question = sentence.question, sentence=sentence)

@app.route("/sentence/<int:sentence_id>/update",methods = ['GET', 'POST'])
@login_required
def update_sentence(sentence_id):
    sentence = Sentence.query.get_or_404(sentence_id)
    if sentence.author != current_user:
        abort(403)
    form = SentenceForm()
    if form.validate_on_submit():
        sentence.question = form.question.data
        sentence.answer = form.answer.data
        db.session.commit()
        flash('Your question has been updated','success')
        return redirect (url_for('sentence',sentence_id=sentence.id))
    elif request.method =='GET':
        form.question.data = sentence.question
        form.question.answer = sentence.answer
    return render_template('create_question.html', title = 'Update Question', form = form, legend='Update Question')
@app.route("/sentence/<int:sentence_id>/delete",methods = ['POST'])
@login_required
def delete_sentence(sentence_id):
    sentence = Sentence.query.get_or_404(sentence_id)
    if sentence.author != current_user:
        abort(403)
    db.session.delete(sentence)
    db.session.commit()
    flash('Your question has been deleted','success')
    return redirect (url_for('questions'))
