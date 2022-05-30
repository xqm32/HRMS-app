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
    db = get_db()
    return render_template("admin/index.html")


@bp.route("/user/modify", methods=["GET", "POST"])
@login_required
def modify():
    immutable_info = {"用户编号", "用户类型", "权限"}
    if request.method == "POST":
        pass

    return render_template("admin/user/modify.html", immutable_info=immutable_info)
