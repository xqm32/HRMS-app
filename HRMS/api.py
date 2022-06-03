from flask import Blueprint, jsonify

from HRMS.auth import login_required
from HRMS.db import get_db
from HRMS.utils import select

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/department/count", methods=["GET"])
@login_required
def department_count():
    db = get_db()

    count = db.execute("SELECT * FROM 部门人数视图").fetchall()

    ret = {"department": select(count, "部门名称"), "count": select(count, "部门人数")}

    return jsonify(ret)


@bp.route("/department/title_count/<department>", methods=["GET"])
@login_required
def title_count(department):
    db = get_db()

    level = db.execute("SELECT DISTINCT 职称等级 FROM 职称信息表").fetchall()
    level = select(level, "职称等级")

    total = 0
    count = []
    for i in level:
        c = db.execute(
            "SELECT COUNT(DISTINCT 职工编号) AS COUNT FROM 职工职称视图 WHERE 部门编号=? AND 职称等级=?",
            (department, i),
        ).fetchone()

        total += c["COUNT"]

        count.append(c["COUNT"])

    if total == 0:
        return {"code": "error"}

    color = [hex(hash(i) % 0xFFFFFF).replace("0x", "#") for i in level]

    ret = {
        "labels": level,
        "datasets": [
            {
                "data": count,
                "backgroundColor": color,
            }
        ],
    }

    return {"code": "success", "data": ret}
