from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = '$2b$12$R8uK1vuXKmX51W22xArRbOrAIkQzSKzhQ5p0cerld52JfCT83SS0O'
db = SQLAlchemy(app)

from flaskserver import routes