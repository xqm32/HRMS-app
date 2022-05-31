from typing import Dict, Iterable

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

from HRMS.auth import login_required
from HRMS.db import get_db

bp = Blueprint("admin", __name__)


@bp.route("/")
@login_required
def index():
    return render_template("admin/index.html")


def get_columns(table: str):
    db = get_db()
    table_schema = db.execute(f"PRAGMA table_info({table})").fetchall()
    table_columns = [row["name"] for row in table_schema]
    return table_columns


# TODO immutable_columns 从 config.py 中读取，如 immutable_columns[table]
def update_table(
    table: str,
    immutable_columns: Iterable[str],
    form: Dict,
    where_clause: str,
    message=(),
):
    db = get_db()
    table_columns = get_columns(table)

    for i in immutable_columns:
        if i in table_columns:
            table_columns.remove(i)

    set_clause = ", ".join(f"{i} = ?" for i in table_columns)

    print(f"UPDATE {table} SET {set_clause} WHERE {where_clause}")
    print(f"{list(form[i] for i in table_columns)}")

    try:
        db.execute(
            f"UPDATE {table} SET {set_clause} WHERE {where_clause}",
            [form[i] for i in table_columns],
        )
        db.commit()
    except Exception as e:
        flash(e, "error")
    else:
        if message:
            flash(*message)


@bp.route("/user/modify", methods=["GET", "POST"])
@login_required
def modify():
    db = get_db()

    immutable_columns = {"用户编号", "用户类型", "权限", "用户名"}
    input_types = {"密码": "password"}

    if request.method == "POST":
        if request.form["table"] == "user_info":
            update_table(
                "用户信息表",
                immutable_columns,
                request.form,
                f"用户编号 = {g.user['用户编号']}",  # 用户编号不从 form 中读取，这样可以不进行鉴权
                message=("信息修改成功", "success"),
            )

            g.user_info = db.execute(
                "SELECT * FROM 用户信息表 WHERE 用户编号 = ?", (g.user["用户编号"],)
            ).fetchone()
        elif request.form["table"] == "user":
            form = dict(request.form)
            form["密码"] = generate_password_hash(form["密码"])

            update_table(
                "用户验证表",
                immutable_columns,
                form,
                f"用户编号 = {g.user['用户编号']}",  # 用户编号不从 form 中读取，这样可以不进行鉴权
            )

            session.clear()

            flash("密码修改成功，请重新登录", "success")

            return redirect(url_for("index"))

    user = dict(g.user)
    user.update({"密码": ""})
    user_info = dict(g.user_info)
    table = {"user": user, "user_info": user_info}

    return render_template(
        "admin/user/modify.html",
        table=table,
        input_types=input_types,
        immutable_columns=immutable_columns,
    )
