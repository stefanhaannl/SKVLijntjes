from flask import Flask, jsonify, flash, request, redirect, url_for, render_template, get_flashed_messages
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from forms import LoginForm, SignUpForm, AddLineForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import and_, or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SKVlijntjes.sqlite3'
app.config['SECRET_KEY'] = "random stringwfds"

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    password = db.Column(db.String(128))
    club = db.Column(db.String(128))
    lines = db.relationship('Line', primaryjoin="or_(User.id==Line.user1_id, User.id==Line.user2_id)", lazy='dynamic')
    #submittedlines = db.relationship('Line')

    def __repr__(self):
        return '<User {} - {}>'.format(self.id, self.name)


class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #usersubmit_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    accepted = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Line {} - {}>'.format(self.user1_id, self.user2_id)


#db.create_all()
#db.session.add(User(name='Stefan Haan',email='stefanhaannl@gmail.com',password='5scZie',club='SKV Amsterdam'))
#db.session.commit()
print(User.query.all())
print(Line.query.all())


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or user.password != form.password.data:
            flash("Username or password incorrect.", "error")
            return redirect(url_for('login'))
        print('User login: {}'.format(user.name))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first() is None:
            newuser = User(name=form.name.data, email=form.email.data, password=form.password.data, club='SKV Amsterdam')
            db.session.add(newuser)
            db.session.commit()
            print('User creation: {}'.format(newuser.name))
            login_user(newuser, remember=0)
            flash("User succesfully created", "mes")
            return redirect(url_for('index'))
        flash("E-mail already exists in the database.", "error")
        return redirect(url_for('signup'))
    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/addline', methods=['GET', 'POST'])
@login_required
def addline():
    form = AddLineForm()
    users = [(user.id, user.name) for user in User.query.all()]
    form.user1.choices = users
    form.user2.choices = users
    if form.validate_on_submit():
        if form.user1.data == form.user2.data:
            flash("You cannot have a line with yourself.", "error")
            return redirect(url_for('addline'))
        if Line.query.filter(or_(and_(Line.user1_id == form.user1.data, Line.user2_id == form.user2.data), and_(Line.user1_id == form.user1.data, Line.user2_id == form.user2.data))).first() is None:
            newline = Line(description=form.description.data, user1_id=form.user1.data, user2_id=form.user2.data)
            db.session.add(newline)
            db.session.commit()
            flash("Line succesfully created", "mes")
            return redirect(url_for('index'))
        else:
            flash("This line already exists.", "error")
            return redirect(url_for('addline'))
    return render_template('addline.html', form=form)

@app.route('/user/<id>')
@login_required
def user(id):
    user = User.query.get(id)
    lines = []
    for line in user.lines:
        lst = [line.user1_id, line.user2_id]
        lst.remove(int(id))
        lines.append(User.query.get(lst[0]).name)
    return render_template('user.html', user=user, lines=lines)


@app.route('/highscores')
@login_required
def highscores():
    pass

app.run(port=5000)
