from typing import Dict, Iterable

from flask import flash

from HRMS.db import get_db


def select(table, column_name, when=None):
    if when:
        return [i[column_name] for i in table if when(i)]
    else:
        return [i[column_name] for i in table]


def to_where_clause(args):
    return " AND".join(f" {i}={args[i]}" for i in args)


def to_args(columns, row):
    return "&".join(f"{j}={str(row[j])}" for j in columns)


def get_columns(table_name: str, with_pk=False, with_fk=False, with_notnull=False):
    db = get_db()
    ret = dict()

    table_schema = table_info(table_name)

    table_columns = select(table_schema, "name")
    ret.update({"columns": table_columns})

    if with_pk:
        table_pk = select(table_schema, "name", lambda i: i["pk"])
        ret.update({"pk": table_pk})

    if with_fk:
        table_fk = foregin_key_list(table_name)
        ret.update({"fk": table_fk})
    
    if with_notnull:
        table_notnull = select(table_schema, "name", lambda i: i["notnull"])
        ret.update({"notnull": table_notnull})

    return ret


def table_info(table_name):
    db = get_db()
    table_info = db.execute(f"PRAGMA table_info({table_name})").fetchall()
    return table_info


def table_xinfo(table_name):
    db = get_db()
    table_xinfo = db.execute(f"PRAGMA tablex_info({table_name})").fetchall()
    return table_xinfo


def foregin_key_list(table_name: str):
    db = get_db()
    table_fk = db.execute(f"PRAGMA foreign_key_list({table_name})").fetchall()
    return table_fk


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
    except db.IntegrityError:
        flash("数据库错误", "error")
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
    except db.IntegrityError:
        flash("数据库错误", "error")
    else:
        if message:
            flash(*message)
