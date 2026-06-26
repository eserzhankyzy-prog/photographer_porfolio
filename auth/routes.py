from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from models import Order, Review, ROLES, User, db, log_action


auth_bp = Blueprint("auth", __name__)
STAFF_ROLES = ("admin", "manager", "employee", "moderator")


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role in STAFF_ROLES:
            return redirect(url_for(f"{current_user.role}.dashboard"))
        return redirect(url_for("auth.profile"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = "client"

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("duplicate_user", "danger")
            return render_template("register.html", roles=ROLES), 409

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role,
        )

        db.session.add(user)
        log_action(f"Registered user {email} as {role}")
        db.session.commit()

        flash("register_success", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", roles=ROLES)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter(func.lower(User.email) == email).first()

        if not user or not check_password_hash(user.password, password):
            flash("invalid_login", "danger")
            return render_template("login.html"), 401

        login_user(user)
        log_action(f"User {user.email} logged in")
        db.session.commit()
        flash("login_success", "success")

        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)

        return redirect(url_for("home"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        log_action(f"User {current_user.email} logged out")
        db.session.commit()
    logout_user()
    flash("logout_success", "success")
    return redirect(url_for("home"))


@auth_bp.route("/profile")
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(
        Order.order_date.desc()
    ).all()
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(
        Review.created_at.desc()
    ).all()
    return render_template("profile.html", orders=orders, reviews=reviews)
