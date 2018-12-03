from flask import Flask, jsonify, flash, request, redirect, url_for, render_template, get_flashed_messages
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from forms import LoginForm, AddUserForm, AddLineForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import and_, or_
import messages as msg

init_db = False

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SKVlijntjes.sqlite3'
app.config['SECRET_KEY'] = "random stringwfds"
masterpassword = 'skvlijntjes'

db = SQLAlchemy(app)

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    users = db.relationship("User")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    password = db.Column(db.String(128))
    club = db.Column(db.Integer, db.ForeignKey('club.id'))
    status = db.Column(db.Integer, default=0)
    lines = db.relationship('Line', primaryjoin="or_(User.id==Line.user1_id, User.id==Line.user2_id)", lazy='dynamic')


class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    accepted = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)


if init_db:
    db.create_all()
    cl = Club(name='SKV Amsterdam')
    db.session.add(cl)
    db.session.commit()
    db.session.add(User(name='Stefan Haan', email='stefanhaannl@gmail.com', password='termacnofas', club=cl.id, status=3))
    db.session.commit()


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
            flash(msg.Error.emailpassincorrect, "error")
            return redirect(url_for('login'))
        print('User login: {}'.format(user.name))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/addline', methods=['GET', 'POST'])
@login_required
def addline():
    form = AddLineForm()
    users = [(user.id, Club.query.get(user.club).name+' - '+user.name) for user in User.query.all()]
    form.user1.choices = users
    form.user2.choices = users
    if form.validate_on_submit():
        if form.user1.data == form.user2.data:
            flash(msg.Error.linewithself, "error")
            return redirect(url_for('addline'))
        if Line.query.filter(or_(and_(Line.user1_id == form.user1.data, Line.user2_id == form.user2.data),
                                 and_(Line.user1_id == form.user2.data, Line.user2_id == form.user1.data))).first() is None:
            if current_user.status >= 2:
                newline = Line(description=form.description.data,
                               user1_id=form.user1.data,
                               user2_id=form.user2.data,
                               accepted=1)
                flash(msg.Message.linecreated, "mes")
            else:
                newline = Line(description=form.description.data,
                               user1_id=form.user1.data,
                               user2_id=form.user2.data,
                               accepted=0)
                flash(msg.Message.linerequested, "mes")
            db.session.add(newline)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash(msg.Error.lineexists, "error")
            return redirect(url_for('addline'))
    return render_template('addline.html', form=form)


@app.route('/user/<id>', methods=['GET','POST'])
@login_required
def user(id):
    form_adduser = AddUserForm()
    clubs = [(club.id, club.name) for club in Club.query.all()]
    form_adduser.club.choices = clubs
    user = User.query.get(id)
    lines = []
    for line in user.lines:
        lst = [line.user1_id, line.user2_id]
        lst.remove(int(id))
        lines.append([User.query.get(lst[0]).name, line.description])
    if current_user.id == int(id):
        if form_adduser.validate_on_submit():
            newuser = User(name=form_adduser.name.data, email=form_adduser.email.data, password=masterpassword, club=form_adduser.club.data, status=0)
            db.session.add(newuser)
            db.session.commit()
            flash(msg.Message.usercreated, "mes")
            return redirect(url_for('index'))
    return render_template('user.html', user=user, lines=lines, form_adduser=form_adduser)


@app.route('/highscores')
@login_required
def highscores():
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'id': user.id,
            'name': user.name,
            'count': Line.query.filter(or_(Line.user1_id == user.id, Line.user2_id == user.id)).count()
            })
    scores = sorted(output, key=lambda x: x['count'])
    return render_template('highscores.html', scores=scores)


app.run(port=5000)
