from app import login_manager, db
from flask_login import UserMixin
from datetime import datetime,timezone


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(100), unique = True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_photo = db.Column(db.String(255), nullable=True, default='default_profile.jpg')
    

    def __repr__(self):
        return f'<User: {self.username}>'
    
    def get_id(self):
        return self.id
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    blog_image = db.Column(db.String(255), nullable=True, default='default_blog_image.jpg')
    
    # Foreign Key to link the Post with the User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    #author access
    author = db.relationship('User', backref='posts', lazy=True)
    # One-to-many relationship with Comment
    comments = db.relationship('Comment', backref='post_comments', lazy=True)

    # One-to-many relationship with Like
    likes = db.relationship('Like', backref='post_likes', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to the User model
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)  # Link to the Post model

    user = db.relationship('User', backref='comments', lazy=True)  # Get the user who made the comment
    post = db.relationship('Post', backref='post_comments', lazy=True)  # Get the post related to the comment


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    user = db.relationship('User', backref='likes', lazy=True)
    post = db.relationship('Post', backref='post_likes', lazy=True)