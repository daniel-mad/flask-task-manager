from datetime import datetime
from flaskserver import db

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(20), nullable=False)
  last_name = db.Column(db.String(20), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  tasks = db.relationship('Todo', backref='owner', lazy=True)
  friend = db.relationship('Followers',lazy=True,
                            primaryjoin='User.id == Followers.user_id', backref='owner')

  def __repr__(self) -> str:
      return f"User({self.id}, {self.first_name}, {self.last_name}, {self.email} )"
      
class Todo(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(200), nullable=False)
  date_time = db.Column(db.DateTime, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

  def __repr__(self) -> str:
      return f"Task({self.id}, {self.date_time}, {self.user_id})"

class Followers(db.Model):
  __tablename__ = 'followers'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  other_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  def __repr__(self) -> str:
      return f"Followers({self.id}, {self.user_id}, {self.other_user_id})"