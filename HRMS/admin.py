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


def select(table, column_name, when=None):
    if when:
        return [i[column_name] for i in table if when(i)]
    else:
        return [i[column_name] for i in table]


def to_where_clause(args):
    return " AND".join(f" {i}={args[i]}" for i in args)


def to_args(columns, row):
    return "&".join(f"{j}={str(row[j])}" for j in columns)


def get_columns(table: str, with_pk=False, with_fk=False):
    db = get_db()
    ret = dict()

    table_schema = db.execute(f"PRAGMA table_info({table})").fetchall()

    table_columns = select(table_schema, "name")
    ret.update({"columns": table_columns})

    if with_pk:
        table_pk = select(table_schema, "name", lambda i: i["pk"])
        ret.update({"pk": table_pk})

    if with_fk:
        table_fk = db.execute(f"PRAGMA foreign_key_list({table})").fetchall()
        ret.update({"fk": table_fk})

    return ret


def create_table(
    table: str,
    immutable_columns: Iterable[str],
    form: Dict,
    message=(),
):
    db = get_db()
    table_columns = get_columns(table)["columns"]

    for i in immutable_columns:
        if i in table_columns:
            table_columns.remove(i)

    columns = ", ".join(f"{i}" for i in table_columns)
    values = ", ".join(f"?" for i in table_columns)

    print(f"INSERT INTO {table}({columns}) VALUES ({values})")
    print(f"{list(form[i] for i in table_columns)}")

    try:
        db.execute(
            f"INSERT INTO {table}({columns}) VALUES ({values})",
            [form[i] for i in table_columns],
        )
        db.commit()
    except Exception as e:
        flash(e, "error")
    else:
        if message:
            flash(*message)


def update_table(
    table: str,
    immutable_columns: Iterable[str],
    form: Dict,
    where_clause: str,
    message=(),
):
    db = get_db()
    table_columns = get_columns(table)["columns"]

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


@bp.route("/user/update", methods=["GET", "POST"])
@login_required
def user_update():
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
        "admin/user/update.html",
        table=table,
        input_types=input_types,
        immutable_columns=immutable_columns,
    )


@bp.route("/create/<table_name>", methods=["GET", "POST"])
@login_required
def create(table_name):
    ret = get_columns(table_name, with_pk=True, with_fk=True)
    table_columns = ret["columns"]
    table_pk = ret["pk"]
    table_fk = select(ret["fk"], "from")
    immutable_columns = []

    # 去除自动编号
    for i in table_pk:
        if "编号" in i and i not in table_fk:
            immutable_columns.append(i)

    if request.method == "POST":
        create_table(table_name, immutable_columns, request.form, ("添加成功", "success"))
        return redirect(url_for("admin.retrieve", table_name=table_name))

    return render_template(
        "admin/create-base.html",
        title="添加信息",
        table_name=table_name,
        columns=table_columns,
        immutable_columns=immutable_columns,
    )


@bp.route("/retrieve/<table_name>", methods=["GET"])
@login_required
def retrieve(table_name):
    db = get_db()

    content = db.execute(f"SELECT * FROM {table_name}").fetchall()
    ret = get_columns(table_name, with_pk=True)
    table_columns = ret["columns"]
    table_pk = ret["pk"]

    header = table_columns
    content = [
        {"row": i, "pk": "&".join(f"{j}={str(i[j])}" for j in table_pk)}
        for i in content
    ]

    return render_template(
        "admin/retrieve-base.html",
        title=table_name,
        table_name=table_name,
        header=header,
        content=content,
    )


@bp.route("/update/<table_name>", methods=["GET", "POST"])
@login_required
def update(table_name):
    db = get_db()
    ret = get_columns(table_name, with_pk=True)
    table_pk = ret["pk"]

    if request.method == "POST":
        update_table(
            table_name,
            table_pk,
            request.form,
            to_where_clause(request.args),
            ("修改成功", "success"),
        )
        return redirect(url_for("admin.retrieve", table_name=table_name))

    row = db.execute(
        f"SELECT * FROM {table_name} WHERE {to_where_clause(request.args)}"
    ).fetchone()

    if row is None:
        abort(404)

    return render_template(
        "admin/update-base.html",
        title="修改信息",
        table_name=table_name,
        row=row,
        immutable_columns=table_pk,
    )


@bp.route("/delete/<table_name>", methods=["GET"])
@login_required
def delete(table_name):
    db = get_db()

    try:
        db.execute(f"DELETE FROM {table_name} WHERE {to_where_clause(request.args)}")
        db.commit()
    except Exception as e:
        flash(e, "error")
    else:
        flash("删除成功", "success")

    return redirect(url_for("admin.retrieve", table_name=table_name))
