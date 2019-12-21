from application import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from application import login
from sqlalchemy import desc

@login.user_loader
def load_user(id):
    return Customer.query.get(int(id))


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('customer.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('customer.id'))
)


class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140), default=None, nullable=True)
    userpic = db.Column(db.String(60), default='default_.jpg', nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comments', backref='author', lazy='dynamic')
    followed = db.relationship(
        'Customer', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<Customer {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = Likes(customer_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            Likes.query.filter_by(
                customer_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return Likes.query.filter(
            Likes.customer_id == self.id,
            Likes.post_id == post.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140), default="")
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    photo = db.Column(db.String(60), nullable=False)
    likes = db.relationship('Likes', backref='post', lazy='dynamic')
    comments = db.relationship('Comments', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def get_comment(self, id):
        return Comments.query.filter_by(post_id=id).order_by(desc(Comments.timestamp)).limit(2)


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Likes {}>'.format(self.username)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Comments {}>'.format(self.username)

