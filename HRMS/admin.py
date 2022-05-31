from typing import Dict, Iterable
import maya, datetime

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


@bp.route("/")
@login_required
def index():
    db = get_db()

    department_count = db.execute("SELECT COUNT(*) AS COUNT FROM 部门信息表").fetchone()
    employee_count = db.execute("SELECT COUNT(*) AS COUNT FROM 员工基本信息表").fetchone()

    attendance_count = db.execute(
        "SELECT COUNT(*) AS COUNT FROM 考勤信息表 WHERE 考勤日期 = ?",
        (maya.now().datetime(to_timezone="Asia/Shanghai").strftime("%Y-%m-%d"),),
    ).fetchone()
    try:
        attendance_rate = f"{attendance_count['COUNT']/employee_count['COUNT']*100:.2f}"
    except ZeroDivisionError:
        attendance_rate = "0.00"
    
    wages_sum = db.execute(
        "SELECT SUM(应发工资) AS SUM FROM 工资计发信息表 WHERE 计发日期 = ?",
        (maya.now().datetime(to_timezone="Asia/Shanghai").strftime("%Y-%m"),),
    ).fetchone()
    if wages_sum["SUM"] is None:
        total_wages = "0.00"
    else:
        total_wages = f"{wages_sum['SUM']:.2f}"

    table = {
        "部门数量": department_count["COUNT"],
        "员工数量": employee_count["COUNT"],
        "计发工资": total_wages,
        "考勤率": attendance_rate,
    }

    return render_template("admin/index.html", table=table)


@bp.route("/user/modify", methods=["GET", "POST"])
@login_required
def modify():
    db = get_db()

    immutable_columns = {"用户编号", "用户类型", "权限", "用户名"}
    input_types = {"密码": "password", "邮箱": "email"}

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
            if form["密码"] == form["确认密码"]:
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
            else:
                flash("两次输入密码不一致", "error")

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
