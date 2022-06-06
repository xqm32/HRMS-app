# 人力资源管理系统

[English](README.md) | 中文

## 使用方法

Linux 上 (需要 sqlite3 >= 3.33.0)

```bash
pip3 install -r requirements
flask init-db
flask run
```

Windows 上

```bash
pip install -r requirements
flask init-db
flask run
```

## 功能

### 基本功能

- [x] 管理部门、职务、职称和其他信息；
- [x] 管理职工信息；
- [x] 管理职工学习经历和工作经历；
- [x] 管理职工家庭关系；
- [x] 管理奖惩信息；
- [x] 部门, 职称信息的查询统计；
- [x] 查询各个部门各个职称的人数（内置）；
- [x] 查询职工编号、姓名、部门和职务信息；
- [x] 等增加、删除、修改职工部门信息的时候自动修改部门人数；
- [x] 数据备份和数据回复。

### 增强功能

- [x] 个人信息管理；
- [x] 用户注册登录；
- [x] 哈希化用户密码保证安全性。
