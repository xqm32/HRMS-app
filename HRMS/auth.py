import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from HRMS.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db()
            .execute("SELECT * FROM 用户验证表 WHERE 用户编号 = ?", (user_id,))
            .fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        realname = request.form["realname"]
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not realname:
            error = "请输入真实姓名"
        elif not username:
            error = "请输入用户名"
        elif not password:
            error = "请输入密码"

        if error is None:
            try:
                db.execute(
                    "INSERT INTO 用户验证表 (用户名, 密码) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()

                user = db.execute(
                    "SELECT * FROM 用户验证表 WHERE 用户名 = ?", (username,)
                ).fetchone()
                user_id = user["用户编号"]

                db.execute(
                    "INSERT INTO 用户信息表 (用户编号, 真实姓名) VALUES (?, ?)",
                    (
                        user_id,
                        realname,
                    ),
                )
                db.commit()
            except db.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"用户名 {username} 已注册"
            else:
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute("SELECT * FROM 用户验证表 WHERE 用户名 = ?", (username,)).fetchone()

        if user is None:
            error = "用户名错误"
        elif not check_password_hash(user["密码"], password):
            error = "密码错误"

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["用户编号"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))
