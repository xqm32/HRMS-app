BEGIN TRANSACTION;
DROP TABLE IF EXISTS "用户验证表";
CREATE TABLE IF NOT EXISTS "用户验证表" (
	"用户编号"	INTEGER NOT NULL UNIQUE,
	"用户名"	TEXT NOT NULL UNIQUE,
	"密码"	TEXT NOT NULL,
	PRIMARY KEY("用户编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "职工家庭表";
CREATE TABLE IF NOT EXISTS "职工家庭表" (
	"职工编号"	INTEGER NOT NULL,
	"关系名称"	TEXT NOT NULL,
	"亲属姓名"	TEXT NOT NULL,
	"联系方式"	TEXT,
	"工作单位"	TEXT,
	FOREIGN KEY("职工编号") REFERENCES "职工信息表"("职工编号"),
	PRIMARY KEY("职工编号","关系名称")
);
DROP TABLE IF EXISTS "部门信息表";
CREATE TABLE IF NOT EXISTS "部门信息表" (
	"部门编号"	INTEGER NOT NULL UNIQUE,
	"部门名称"	TEXT NOT NULL UNIQUE,
	"主管人员"	INTEGER,
	"下属人数"	INTEGER NOT NULL DEFAULT 0,
	"联系方式"	TEXT,
	"所在地址"	TEXT,
	PRIMARY KEY("部门编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "职工信息表";
CREATE TABLE IF NOT EXISTS "职工信息表" (
	"职工编号"	INTEGER NOT NULL UNIQUE,
	"职工姓名"	TEXT NOT NULL,
	"职工性别"	TEXT CHECK("职工性别" IN (NULL, "男", "女")),
	"身份证号"	TEXT UNIQUE,
	"电子邮件"	TEXT,
	"联系方式"	TEXT,
	"联系地址"	TEXT,
	"入职日期"	TEXT,
	PRIMARY KEY("职工编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "职工职称表";
CREATE TABLE IF NOT EXISTS "职工职称表" (
	"职工编号"	INTEGER NOT NULL,
	"职称名称"	TEXT NOT NULL,
	"起始日期"	TEXT,
	FOREIGN KEY("职工编号") REFERENCES "职工信息表"("职工编号"),
	FOREIGN KEY("职称名称") REFERENCES "职称信息表"("职称名称"),
	PRIMARY KEY("职工编号","职称名称")
);
DROP TABLE IF EXISTS "职称信息表";
CREATE TABLE IF NOT EXISTS "职称信息表" (
	"职称名称"	TEXT NOT NULL UNIQUE,
	"职称等级"	TEXT NOT NULL,
	"职称系列"	TEXT,
	"职称要求"	TEXT,
	PRIMARY KEY("职称名称")
);
DROP TABLE IF EXISTS "用户信息表";
CREATE TABLE IF NOT EXISTS "用户信息表" (
	"用户编号"	INTEGER NOT NULL UNIQUE,
	"用户姓名"	TEXT NOT NULL,
	"身份证号"	TEXT UNIQUE,
	"电子邮件"	TEXT,
	"联系方式"	TEXT,
	"联系地址"	TEXT,
	"注册日期"	TEXT,
	FOREIGN KEY("用户编号") REFERENCES "用户验证表"("用户编号"),
	PRIMARY KEY("用户编号")
);
DROP TABLE IF EXISTS "职务信息表";
CREATE TABLE IF NOT EXISTS "职务信息表" (
	"职务编号"	INTEGER NOT NULL UNIQUE,
	"职务名称"	TEXT NOT NULL,
	"所在部门"	INTEGER NOT NULL,
	"基础薪资"	REAL DEFAULT 1000,
	"最高薪资"	REAL DEFAULT 1000000,
	FOREIGN KEY("所在部门") REFERENCES "部门信息表"("部门编号"),
	PRIMARY KEY("职务编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "个人信息表";
CREATE TABLE IF NOT EXISTS "个人信息表" (
	"身份证号"	TEXT NOT NULL UNIQUE,
	"姓名"	INTEGER,
	"性别"	INTEGER,
	"出生日期"	TEXT,
	"民族"	INTEGER,
	"籍贯"	INTEGER,
	PRIMARY KEY("身份证号")
);
DROP TABLE IF EXISTS "工作经历表";
CREATE TABLE IF NOT EXISTS "工作经历表" (
	"职工编号"	INTEGER NOT NULL,
	"所在单位"	TEXT NOT NULL,
	"就任职务"	TEXT,
	"最高职称"	TEXT,
	"起始日期"	TEXT NOT NULL,
	"结束日期"	TEXT,
	FOREIGN KEY("职工编号") REFERENCES "职工信息表"("职工编号"),
	PRIMARY KEY("职工编号","所在单位","起始日期")
);
DROP TABLE IF EXISTS "学习经历表";
CREATE TABLE IF NOT EXISTS "学习经历表" (
	"职工编号"	INTEGER NOT NULL,
	"所在院校"	TEXT NOT NULL,
	"所修学位"	TEXT,
	"就读专业"	TEXT,
	"起始日期"	TEXT NOT NULL,
	"结束日期"	TEXT,
	FOREIGN KEY("职工编号") REFERENCES "职工信息表"("职工编号"),
	PRIMARY KEY("职工编号","所在院校","起始日期")
);
DROP TABLE IF EXISTS "职工职务表";
CREATE TABLE IF NOT EXISTS "职工职务表" (
	"职工编号"	INTEGER NOT NULL,
	"职务编号"	INTEGER NOT NULL,
	"起始日期"	TEXT NOT NULL,
	"结束日期"	TEXT,
	FOREIGN KEY("职工编号") REFERENCES "职工信息表"("职工编号"),
	FOREIGN KEY("职务编号") REFERENCES "职务信息表"("职务编号"),
	PRIMARY KEY("职工编号","职务编号","起始日期")
);
DROP TABLE IF EXISTS "职工奖惩表";
CREATE TABLE IF NOT EXISTS "职工奖惩表" (
	"奖惩编号"	INTEGER NOT NULL UNIQUE,
	"职工编号"	INTEGER NOT NULL,
	"奖惩类型"	TEXT NOT NULL,
	"奖惩日期"	TEXT NOT NULL,
	"奖惩数额"	REAL NOT NULL DEFAULT 0,
	"奖惩原因"	TEXT,
	FOREIGN KEY("职工编号") REFERENCES "职工信息表"("职工编号"),
	PRIMARY KEY("奖惩编号" AUTOINCREMENT)
);
DROP INDEX IF EXISTS "身份证号索引";
CREATE INDEX IF NOT EXISTS "身份证号索引" ON "用户信息表" (
	"身份证号"
);
DROP INDEX IF EXISTS "职工身份证唯一索引";
CREATE INDEX IF NOT EXISTS "职工身份证唯一索引" ON "职工信息表" (
	"身份证号"
);
DROP TRIGGER IF EXISTS "删除用户触发器";
CREATE TRIGGER 删除用户触发器 AFTER DELETE 
ON 用户信息表
BEGIN
    DELETE FROM 用户验证表 WHERE 用户编号 = old.用户编号;
END;
DROP VIEW IF EXISTS "部门人数视图";
CREATE VIEW 部门人数视图 AS
SELECT 
部门编号,
部门名称,
COUNT(DISTINCT 职工编号) AS 部门人数
FROM 职工职务视图
GROUP BY 部门编号;
DROP VIEW IF EXISTS "职工职务视图";
CREATE VIEW 职工职务视图 AS
SELECT 职工信息表.职工编号, 职工姓名, 职工职务表.职务编号,职务名称,部门编号,部门名称
FROM 职工信息表, 职工职务表, 职务信息表, 部门信息表
WHERE 职工信息表.职工编号 = 职工职务表.职工编号 AND 职务信息表.职务编号=职工职务表.职务编号 AND 职务信息表.所在部门=部门信息表.部门编号;
DROP VIEW IF EXISTS "职工职称视图";
CREATE VIEW 职工职称视图 AS
SELECT 职工职务视图.职工编号, 职工姓名, 职务编号,职务名称,部门编号,部门名称, 职工职称表.职称名称, 职称等级
FROM 职工职务视图, 职工职称表, 职称信息表
WHERE 职工职务视图.职工编号=职工职称表.职工编号 AND 职工职称表.职称名称=职称信息表.职称名称;
COMMIT;
