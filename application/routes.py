import os
from flask import render_template, flash, redirect, request, url_for
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from application import app, db, ALLOWED_EXTENSIONS
from application.forms import LoginForm, RegistrationForm, EditProfileForm
from application.models import Customer, Post, Comments
from flask_login import current_user, login_user, logout_user, login_required


@app.route('/main/<username>', methods=['GET', 'POST'])
@login_required
def index(username):
    posts = Post.query.order_by(desc(Post.timestamp)).limit(30)
    return render_template('main.html', posts=posts, user=current_user)


@app.route('/', methods=['GET', 'POST'])
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect('/main/' + current_user.username)
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Customer(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/main/' + current_user.username)
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/main/' + current_user.username)
    form = LoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect('login')
        login_user(user, remember=form.remember_me.data)
        return redirect('/main/' + current_user.username)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('login')


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = Customer.query.filter_by(username=username).first_or_404()
    userpic = url_for('static', filename=user.userpic)
    posts = Post.query.filter_by(customer_id=user.id)
    return render_template('profile.html', user=user, userpic=userpic, posts=posts)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if request.method == 'POST':
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.userpic = filename
        db.session.commit()
        return redirect('/user/' + current_user.username)
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('editProfile.html', title='Edit Profile',
                           form=form)


@app.route('/add_photo', methods=['GET', 'POST'])
def add_photo():
    if request.method == 'POST':
        description = request.form['description']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post = Post(body=description, customer_id=current_user.id, photo=filename)
            db.session.add(post)
            db.session.commit()
        return redirect('/user/' + current_user.username)
    return '''
<html>
<head>

</head>
<body>
    <h1>Add new post</h1>
    <form action="" method = post enctype = multipart/form-data>
        <p>
            <input type=text name=description>
        </p>
        <p><input type=file name=file>
            <input type=submit value=Upload></p>
    </form>
</body>
</html>
'''


@app.route('/like_action')
@login_required
def like_action():
    action = request.args.get('act')
    post_id = request.args.get('post_id')
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    number = post.likes.count()
    print(number)
    return render_template('likes_counter.html', number=number)


@app.route('/follow_action')
@login_required
def follow_action():
    action = request.args.get('act')
    username = request.args.get('username')
    user = Customer.query.filter_by(username=username).first_or_404()
    if action == 'Unfollow':
        current_user.follow(user)
        db.session.commit()
    else:
        current_user.unfollow(user)
        db.session.commit()
    return '''
    '''


@app.route('/add_comment')
@login_required
def add_comment():
    comment = request.args.get('comment')
    post_id = request.args.get('post_id')
    comment = Comments(customer_id=current_user.id, post_id=post_id, comment=comment)
    db.session.add(comment)
    db.session.commit()
    return redirect('/main/' + current_user.username)