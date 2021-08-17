from enum import unique
from functools import reduce
from flask import Flask, render_template, url_for, request, redirect, session, g, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import backref


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = '$2b$12$R8uK1vuXKmX51W22xArRbOrAIkQzSKzhQ5p0cerld52JfCT83SS0O'
db = SQLAlchemy(app)



bcrypt = Bcrypt()


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


@app.route('/' ,methods=['POST', 'GET'])
def index():
  if 'user' and 'username' not in session:
        return redirect(url_for('login'))

  if request.method == 'POST':
        task_content = request.form["content"]
        if not task_content:
          flash("Please enter task content!")
          return redirect(url_for('index'))
        new_task = Todo(content=task_content, user_id=g.user_id)      
        try:
            db.session.add(new_task)
            db.session.commit()
            #redirect is get operation
            return redirect(url_for('index'))
        except:
            return 'Error while add new task!!!'
  else:
        tasks =  Todo.query.filter_by(user_id=g.user_id).order_by(Todo.date_time).all()
        friends = Followers.query.filter_by(other_user_id=g.user_id).all()
        return render_template('index.html', task_in_html=tasks, friends=friends)


@app.route('/register', methods=['POST', 'GET'])
def register():
  if request.method == 'GET':
    return render_template('register.html', title="Register")
  else:
    first_name = request.form['fname']
    last_name = request.form['lname']
    email = request.form['email']
    password = request.form['password']
    password_confirm = request.form['confirm']
    if password != password_confirm:
       return render_template('register.html',
                               title="Register", message="Password not match!", status='danger')
    password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(first_name=first_name, last_name=last_name, email=email.lower(), password=password)
    
    try:
      db.session.add(user)
      db.session.commit()
      user = User.query.filter_by(email=email).first()
      session['user'] = user.id
      session['username'] = f"{user.first_name} {user.last_name}"
      return redirect(url_for('index'))
    except Exception as e:
      print(e)
      return "Error when adding user"

    
    


@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'GET':
    return render_template('login.html', title="Login")
  else:
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email.lower()).first()
    if not user:
      flash("User not found. Please register")
      return render_template('register.html', title="Register")
    if not bcrypt.check_password_hash(user.password, password):
      return render_template('login.html', title="Login",
                               message="Wrong Password", status='danger')
    session['user'] = user.id
    session['username'] = f"{user.first_name} {user.last_name}"
    return redirect(url_for('index'))



@app.route('/delete/<int:id>')
def delete(id):
  if 'user' not in session:
      return redirect(url_for('login'))

  task = Todo.query.get_or_404(id)
  owner_id = task.owner.id
  try:
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index', id=owner_id))
  except:
    return 'Error while delete task!'
  
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
  if 'user' not in session:
      return redirect(url_for('login'))

  task = Todo.query.get_or_404(id)
  if request.method == 'GET':
   return render_template('update.html', task=task)
  else:
    task_update = request.form['content']
    if not task_update:
      flash("Update cannot be empty! ")
      return redirect(url_for('update', id=id))
    try:
       task.content = task_update
       db.session.commit()
       return redirect(url_for('index', id=task.owner.id))
    except:
      return 'Error while update task!'


@app.route('/users')
def users():
  if not g.user_id:
    return redirect(url_for('login'))
  try:
      friends = Followers.query.filter_by(user_id=g.user_id).all()
      friends_ids = [f.other_user_id for f in friends]
      users = User.query.filter(User.id != g.user_id).all()
      return render_template('users.html', users=users, friends=friends_ids)
  except Exception as e:
    print(e)
    return "Error when reading users"

@app.route('/users/<int:other_user_id>')
def allow_user(other_user_id):
  if not g.user_id:
    return redirect(url_for('login'))
  try:
      follow = Followers(user_id=g.user_id, other_user_id=other_user_id)
      db.session.add(follow)
      db.session.commit()
      return redirect(url_for('users'))
  except Exception as e:
    print(e)
    return "Error when allow user"


@app.route('/logout')
def logout():
  session.pop('user', None)
  session.pop('username', None)
  return redirect(url_for('login'))

@app.route('/user/<int:user_id>')
def read_user(user_id):
  if 'user' and 'username' not in session:
        return redirect(url_for('login'))
  
  followers = Followers.query.filter_by(other_user_id=g.user_id).all()
  found = False
  for follow in followers:
    if follow.user_id == user_id:
      found = True
  if not found:
    return redirect(url_for('index'))

  tasks =  Todo.query.filter_by(user_id=user_id).order_by(Todo.date_time).all()
  user = User.query.filter_by(id=user_id).first()
  return render_template('user.html', task_in_html=tasks, user=user)


@app.before_request
def before_request():
  g.user_id = None
  g.user_name = None
  if 'user' and 'username' in session:
    g.user_id = session['user']
    g.username = session['username']
    
  

if __name__ == "__main__":
  app.run(debug=True)
  
 