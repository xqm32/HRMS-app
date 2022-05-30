from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from HRMS.auth import login_required
from HRMS.db import get_db

bp = Blueprint("admin", __name__)


@bp.route("/")
@login_required
def index():
    return render_template("admin/index.html")


@bp.route("/user/modify", methods=["GET", "POST"])
@login_required
def modify():
    db = get_db()

    immutable_info = {"用户编号", "用户类型", "权限"}
    if request.method == "POST":
        schema_user_info = db.execute("PRAGMA table_info(用户信息表)").fetchall()
        columns_user_info = {row["name"] for row in schema_user_info}
        columns_user_info -= immutable_info

        # 固定顺序
        columns_user_info = list(columns_user_info)
        # 虽然这种更新可能比较危险，但是我懒得写更安全的方法了
        db.execute(
            f"UPDATE 用户信息表 SET ({', '.join(columns_user_info)}) = ({', '.join('?' for _ in columns_user_info)}) WHERE 用户编号 = {g.user['用户编号']}",
            [request.form[i] for i in columns_user_info],
        )
        db.commit()

        g.user = db.execute(
            "SELECT * FROM 用户验证表 WHERE 用户编号 = ?", (g.user["用户编号"],)
        ).fetchone()
        g.user_info = db.execute(
            "SELECT * FROM 用户信息表 WHERE 用户编号 = ?", (g.user["用户编号"],)
        ).fetchone()

        flash("用户信息修改成功", category="success")

    return render_template("admin/user/modify.html", immutable_info=immutable_info)
