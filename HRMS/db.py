import shutil
import os
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db

def get_backup():
    if os.path.exists(current_app.config["DATABASE_BACKUP"]):
        os.remove(current_app.config["DATABASE_BACKUP"])

    db = sqlite3.connect(
            current_app.config["DATABASE_BACKUP"], detect_types=sqlite3.PARSE_DECLTYPES
        )
    db.row_factory = sqlite3.Row
    return db

def has_backup():
    return os.path.exists(current_app.config["DATABASE_BACKUP"])

def restore_db():
    # 必须先检查 has_backup()
    if not has_backup():
        return False

    close_db()

    os.remove(current_app.config["DATABASE"])
    shutil.copyfile(current_app.config["DATABASE_BACKUP"], current_app.config["DATABASE"])


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
