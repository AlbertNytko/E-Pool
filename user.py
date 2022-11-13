#this file contains the parent class for the different epool users (drivers and riders)

from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from models import Users, db
from auth import login_manager
from flask_login import login_required, logout_user, current_user, login_user

user = Blueprint("user", __name__, static_folder="static", template_folder="templates")

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.myTickets = []
        self.friendList = []

    def add_friend(self, friend):
        self.friendList.append(friend)
    
    def delete_friend(self, friend):
        self.friendList.remove(friend)

    @user.route("/")
    def home():
        return render_template("index.html")

    @user.route("/register", methods=["POST", "GET"])
    def create_account():
        if request.method == "POST":
            user_email = request.form["email"]
            user_password = request.form["psw"]
            found_user = Users.query.filter_by(email=user_email).first()

            if found_user:
                flash("User exists, please login", 'error')
                return redirect(url_for("user.login"))
            if len(user_password) < 8:
                flash("Password must be at least 8 characters long!", 'warning')
                return render_template("register.html")
            else:
                flash("New account created!", 'success')
                usr = Users(email = user_email)
                usr.set_password(user_password)
                db.session.add(usr)
                db.session.commit()
                return redirect(url_for("user.login"))
        else:
            if current_user.is_authenticated:
                flash("Already Logged In!", 'success')
                return redirect(url_for("user.profile"))
            return render_template("register.html")

    @user.route("/login", methods=["POST", "GET"])
    def login():
        if request.method == "POST":
            user_email = request.form["email"]
            user_password = request.form["psw"]
            found_user = Users.query.filter_by(email=user_email).first()

            if not found_user:
                flash("No user found, please sign up!", 'warning')
                return redirect(url_for("user.create_account"))

            if found_user and found_user.check_password(user_password):
                login_user(found_user)
                flash("Login Successful!", 'success')
                return redirect(url_for("user.profile"))
            
            flash("Password incorrect! Try again.", 'warning')
            return render_template("login.html")
        else:
            if current_user.is_authenticated:
                flash("Already Logged In!", 'success')
                return redirect(url_for("user.profile"))
            return render_template("login.html")

    @user.route("/profile", methods=["POST", "GET"])
    @login_required
    def profile():
        user_email = current_user.email
        users = Users.query.all()
        for user in users:
            print("Email: " + user.email + " Password: " + user.password)
        return render_template("profile.html", email=user_email)

    @user.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out!", 'success')
        return redirect(url_for("user.login"))
    
    @login_manager.user_loader
    def load_user(user_id):
        """Check if user is logged-in on every page load."""
        if user_id is not None:
            return Users.query.get(user_id)
        return None

    @login_manager.unauthorized_handler
    def unauthorized():
        """Redirect unauthorized users to Login page."""
        flash('Please login first!', 'error')
        return redirect(url_for('user.login'))