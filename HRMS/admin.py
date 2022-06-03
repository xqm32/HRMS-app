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
from HRMS.db import get_backup, get_db, has_backup, restore_db
from HRMS.utils import (
    create_table,
    error_i18n,
    get_columns,
    select,
    to_args,
    to_where_clause,
    update_table,
)

bp = Blueprint("admin", __name__)


@bp.route("/")
@login_required
def index():
    db = get_db()

    department_count = db.execute("SELECT COUNT(*) AS COUNT FROM 部门信息表").fetchone()
    employee_count = db.execute("SELECT COUNT(*) AS COUNT FROM 职工信息表").fetchone()
    title_count = db.execute(
        "SELECT COUNT(DISTINCT 职工编号) AS COUNT FROM 职称信息视图"
    ).fetchone()

    title_rate = (
        round(title_count["COUNT"] / employee_count["COUNT"] * 100, 2)
        if employee_count["COUNT"] != 0
        else 0
    )

    department = db.execute("SELECT * FROM 部门信息表").fetchall()
    title = db.execute("SELECT * FROM 职称信息表").fetchall()

    table = {
        "部门数量": department_count["COUNT"],
        "员工数量": employee_count["COUNT"],
        "获职称人数": title_count["COUNT"],
        "获职称比例": title_rate,
        "部门": department,
        "职称": title,
    }

    return render_template("admin/index.html", table=table)


@bp.route("/user/update", methods=["GET", "POST"])
@login_required
def user_update():
    db = get_db()

    immutable_columns = {"用户编号", "用户类型", "权限", "用户名"}
    input_types = {"密码": "password", "电子邮箱": "email", "注册日期": "date"}

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
    db = get_db()

    ret = get_columns(
        table_name, with_pk=True, with_fk=True, with_notnull=True, with_default=True
    )
    header = ret["columns"]
    fk = ret["fk"]

    table_pk = ret["pk"]
    table_fk = select(fk, "from")
    table_notnull = ret["notnull"]
    table_default = ret["default"]

    immutable_columns = []

    input_types = dict()

    # 去除自动编号
    for i in table_pk:
        if "编号" in i and i not in table_fk:
            immutable_columns.append(i)

    for i in header:
        if "人数" in i:
            immutable_columns.append(i)
        if "日期" in i:
            input_types.update({i: "date"})

    selectable_columns = dict()
    for i in fk:
        things = db.execute(f"SELECT * FROM {i['table']}").fetchall()

        name = i["to"]
        id = i["to"]

        if things:
            if i["to"].replace("编号", "名称") in things[0].keys():
                name = i["to"].replace("编号", "名称")
            elif i["to"].replace("编号", "姓名") in things[0].keys():
                name = i["to"].replace("编号", "姓名")

        l = [
            {
                "from": i["from"],
                "name": j[name],
                "id": j[id],
            }
            for j in things
        ]

        selectable_columns.update({i["from"]: l})

    if request.method == "POST":
        create_table(table_name, immutable_columns, request.form, ("添加成功", "success"))
        return redirect(url_for("admin.retrieve", table_name=table_name))

    return render_template(
        "admin/create-base.html",
        title="添加信息",
        table_name=table_name,
        header=header,
        input_types=input_types,
        table_default=table_default,
        immutable_columns=immutable_columns,
        notnull_columns=table_notnull,
        selectable_columns=selectable_columns,
    )


@bp.route("/retrieve/<table_name>", methods=["GET"])
@login_required
def retrieve(table_name):
    db = get_db()

    content = db.execute(f"SELECT * FROM {table_name}").fetchall()
    ret = get_columns(table_name, with_pk=True, with_fk=True)
    table_columns = ret["columns"]
    table_pk = ret["pk"]
    fk = ret["fk"]

    no_edit = False
    if "视图" in table_name:
        no_edit = True

    header = table_columns
    content = [{"row": i, "pk": to_args(table_pk, i)} for i in content]

    selectable_columns = dict()
    for i in fk:
        things = db.execute(f"SELECT * FROM {i['table']}").fetchall()

        name = i["to"]
        id = i["to"]

        if things:
            if i["to"].replace("编号", "名称") in things[0].keys():
                name = i["to"].replace("编号", "名称")
            elif i["to"].replace("编号", "姓名") in things[0].keys():
                name = i["to"].replace("编号", "姓名")

        l = {j[id]: j[name] for j in things}

        selectable_columns.update({i["from"]: l})

    return render_template(
        "admin/retrieve-base.html",
        title=table_name,
        no_edit=no_edit,
        table_name=table_name,
        selectable_columns=selectable_columns,
        header=header,
        content=content,
    )


@bp.route("/update/<table_name>", methods=["GET", "POST"])
@login_required
def update(table_name):
    db = get_db()

    ret = get_columns(table_name, with_pk=True, with_fk=True, with_notnull=True)
    header = ret["columns"]
    fk = ret["fk"]

    table_pk = ret["pk"]
    table_fk = select(fk, "from")
    table_notnull = ret["notnull"]

    immutable_columns = list(table_pk)

    input_types = dict()

    for i in header:
        if "人数" in i:
            immutable_columns.append(i)
        if "日期" in i:
            input_types.update({i: "date"})

    selectable_columns = dict()
    for i in fk:
        things = db.execute(f"SELECT * FROM {i['table']}").fetchall()

        name = i["to"]
        id = i["to"]

        if things:
            if i["to"].replace("编号", "名称") in things[0].keys():
                name = i["to"].replace("编号", "名称")
            elif i["to"].replace("编号", "姓名") in things[0].keys():
                name = i["to"].replace("编号", "姓名")

        l = [
            {
                "from": i["from"],
                "name": j[name],
                "id": j[id],
            }
            for j in things
        ]

        selectable_columns.update({i["from"]: l})

    if request.method == "POST":
        update_table(
            table_name,
            immutable_columns,
            request.form,
            to_where_clause(request.args),
            ("修改成功", "success"),
        )
        return redirect(url_for("admin.retrieve", table_name=table_name))

    content = db.execute(
        f"SELECT * FROM {table_name} WHERE {to_where_clause(request.args)}"
    ).fetchone()

    if content is None:
        abort(404)

    return render_template(
        "admin/update-base.html",
        title="修改信息",
        table_name=table_name,
        content=content,
        input_types=input_types,
        immutable_columns=immutable_columns,
        notnull_columns=table_notnull,
        selectable_columns=selectable_columns,
    )


@bp.route("/delete/<table_name>", methods=["GET"])
@login_required
def delete(table_name):
    db = get_db()

    try:
        db.execute(f"DELETE FROM {table_name} WHERE {to_where_clause(request.args)}")
        db.commit()
    except db.Error as e:
        flash(error_i18n(e.args), "error")
    else:
        flash("删除成功", "success")

    return redirect(url_for("admin.retrieve", table_name=table_name))

@bp.route("/backup", methods=["GET"])
@login_required
def backup():
    db = get_db()
    db_backup = get_backup()

    db.backup(db_backup)
    db_backup.close()
    flash("备份成功", "success")

    return redirect(url_for('index'))

@bp.route("/restore", methods=["GET"])
@login_required
def restore():
    if not has_backup():
        flash("数据库备份不存在", "warning")
        return redirect(url_for('index'))
    else:
        restore_db()
        flash("恢复成功，请重新登录", "success")
        return redirect(url_for('auth.logout'))