from typing import Dict, Iterable

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
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
    success_message=None,
    functions: Dict = {},
):
    db = get_db()
    table_columns = get_columns(table)

    for i in immutable_columns:
        table_columns.remove(i)

    set_clause = ", ".join(f"{i} = ?" for i in table_columns)

    print(f"UPDATE {table} SET {set_clause} WHERE {where_clause}")
    print(f"{list(form[i] for i in table_columns)}")

    try:
        db.execute(
            f"UPDATE {table} SET {set_clause} WHERE {where_clause}",
            [
                functions[i](form[i]) if i in functions else form[i]
                for i in table_columns
            ],
        )
        db.commit()
    except Exception as e:
        flash(e, "error")
    else:
        if success_message:
            flash("修改用户信息成功", "success")


@bp.route("/user/modify", methods=["GET", "POST"])
@login_required
def modify():
    db = get_db()

    immutable_columns = {"用户编号", "用户类型", "权限"}
    if request.method == "POST":
        update_table(
            "用户信息表",
            immutable_columns,
            request.form,
            f"用户编号 = {g.user['用户编号']}",
            success_message="修改用户信息成功",
        )

        g.user_info = db.execute(
            "SELECT * FROM 用户信息表 WHERE 用户编号 = ?", (g.user["用户编号"],)
        ).fetchone()

    return render_template(
        "admin/user/modify.html", immutable_columns=immutable_columns
    )


@bp.route("/user/password", methods=["GET", "POST"])
@login_required
def password():
    db = get_db()

    immutable_columns = {"用户编号", "用户名"}
    input_types = {"密码": "password"}
    if request.method == "POST":
        update_table(
            "用户验证表",
            immutable_columns,
            request.form,
            f"用户编号 = {g.user['用户编号']}",
            success_message="修改用户信息成功",
            functions={"密码": generate_password_hash},
        )

        g.user = db.execute(
            "SELECT * FROM 用户验证表 WHERE 用户编号 = ?", (g.user["用户编号"],)
        ).fetchone()

    user = dict(g.user)
    user.update({"密码": ""})

    return render_template(
        "admin/user/password.html",
        table=user,
        input_types=input_types,
        immutable_columns=immutable_columns,
    )
