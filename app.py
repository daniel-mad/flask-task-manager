from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(20), nullable=False)
  last_name = db.Column(db.String(20), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)
  tasks = db.relationship('Todo', backref='owner', lazy=True)

  def __repr__(self) -> str:
      return f"User({self.id}, {self.first_name}, {self.last_name}, {self.email} )"
      

class Todo(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(200), nullable=False)
  date_time = db.Column(db.DateTime, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

  def __repr__(self) -> str:
      return f"Task({self.id}, {self.date_time}, {self.user_id})"


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
    user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    try:
      db.session.add(user)
      db.session.commit()
      return redirect(url_for('login'))
    except:
      return "Error when adding user"

    
    


@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'GET':
    return render_template('login.html', title="Login")
  else:
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if not user:
      return render_template('register.html',
                               title="Register", message="User not found. Please register", status='danger')
    if user.password != password:
      return render_template('login.html', title="Login",
                               message="Wrong Password", status='danger')
    return redirect(url_for('index', id=user.id))

@app.route('/<int:id>' ,methods=['POST', 'GET'])
def index(id):
    if request.method == 'POST':
        task_content = request.form["content"]
        new_task = Todo(content=task_content, user_id=id)      
        try:
            db.session.add(new_task)
            db.session.commit()
            #redirect is get operation
            return redirect(url_for('index', id=id))
        except:
            return 'Error while add new task!!!'
    else:
        tasks =  Todo.query.filter_by(user_id=id).order_by(Todo.date_time).all()
        return render_template('index.html', task_in_html=tasks, user_id=id)

@app.route('/delete/<int:id>')
def delete(id):
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
  task = Todo.query.get_or_404(id)
  if request.method == 'GET':
   return render_template('update.html', task=task)
  else:
    try:
       task.content = request.form['content']
       db.session.commit()
       return redirect(url_for('index', id=task.owner.id))
    except:
      return 'Error while update task!'


@app.route('/')
def home():
  return redirect(url_for('register'))
    
  

if __name__ == "__main__":
  app.run(debug=True)