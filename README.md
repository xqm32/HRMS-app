# Human Resource Management System

English | [中文](README_zh.md)

## Usage

on Linux (require sqlite3 >= 3.33.0)

```bash
pip3 install -r requirements
flask init-db
flask run
```

on Windows

```bash
pip install -r requirements
flask init-db
flask run
```

## Features

### Basic

- [x] Management of departments, positions, titles and other information;
- [x] Management of employee information;
- [x] Management of employee learning experience and employment experience;
- [x] Management of employee family relations;
- [x] Management of reward and punishment information;
- [x] Department, title information query statistics, etc.
- [x] Query the number of employees with various titles in a department (built-in);
- [x] Query the employee ID, name, department and job information of each employee;
- [x] Automatically modify the number of employees in the corresponding department when adding or deleting employees and modifying employee department information;
- [x] Data backup and data recovery.

### Enhanced

- [x] Management of personal infomation;
- [x] User login and register;
- [x] Hashing user password to ensure security.
