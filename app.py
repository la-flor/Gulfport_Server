import os
from flask import Flask, request, url_for, redirect, jsonify, flash, render_template
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension

from flask_admin import Admin
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
db = SQLAlchemy(app)
CORS(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "you should have a password in your config file")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///gulfport_votes')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.debug = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

from models import User, Event, EventModelView, UserModelView
from forms import LoginForm, CreateUserForm, ResetPasswordForm, RequestResetForm


# instatiate and create admin view to edit events database table
admin = Admin(app)
admin.add_view(EventModelView(Event, db.session))
admin.add_view(UserModelView(User, db.session))

# instantiate and initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

# connects flask-login users with database users
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None

# GET request returns login page with login
# POST request authenticates user and redirects to admin page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You're already logged in.  You may logout or use the links on the toolbar to navigate.", 'info')
        return redirect('/admin')
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            email = form.email.data
            password = form.password.data

            user = User.is_valid(email=email, password=password)
            login_user(user)
            
            flash("You have successfully logged in", "success")
            return redirect("/admin")
        except:
            flash("Invalid login attempt.", 'danger')
            return redirect('/login')

    return render_template('login.html', title="Login Page", form=form)

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have successfully logged out.", 'success')
        return redirect('/admin')
    else:
        flash("You are not currently logged in.  To login, click the 'Login' button for further access.", 'warning')
        return redirect('/admin')

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                    sender='leifaflor@gmail.com',
                    recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
                    {url_for('reset_token', token=token, _external=True)}
                    If you did not make this request then simply ignore this email and no changes will be made.'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('/admin')

    form = RequestResetForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user:    
                send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'success')
            return redirect('/login')
        except:
            flash("An error occured.  Please contact our dev team.", "danger")

    return render_template('request_reset.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('/admin')

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'danger')
        return redirect('/reset_password')

    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            User.change_password(user, form.password.data)
            flash('Your password has been updated.', 'success')
            return redirect('/login')
        except:
            flash('We were unable to update your password.  Please contact our dev team for further assistence.', 'danger')
            return redirect('/reset_password')

    return render_template('reset_token.html', title='Reset Password', form=form, token=token)

@app.route("/events", methods=["GET", "POST"])
def events():
    """Return all events in our database"""

    events = Event.all_events()
    return jsonify(events = events)

@app.errorhandler(404)
def invalid_route(e):
    return render_template('404.html', title="404 Error")