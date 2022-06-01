BEGIN TRANSACTION;
DROP TABLE IF EXISTS "原单位信息表";
CREATE TABLE IF NOT EXISTS "原单位信息表" (
	"员工编号"	INTEGER NOT NULL,
	"原单位"	TEXT,
	"原职称"	TEXT,
	"原职务"	TEXT,
	PRIMARY KEY("员工编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "员工基本信息表";
CREATE TABLE IF NOT EXISTS "员工基本信息表" (
	"员工编号"	INTEGER NOT NULL,
	"姓名"	TEXT NOT NULL,
	"性别"	TEXT NOT NULL,
	"所属部门编号"	TEXT,
	"进入部门日期"	TEXT NOT NULL,
	"职务代码"	TEXT NOT NULL,
	"职称"	TEXT,
	"起薪日"	TEXT,
	"在岗状态"	TEXT NOT NULL,
	PRIMARY KEY("员工编号" AUTOINCREMENT),
	FOREIGN KEY("职务代码") REFERENCES "职务信息表"("职务代码")
);
DROP TABLE IF EXISTS "员工学历信息表";
CREATE TABLE IF NOT EXISTS "员工学历信息表" (
	"员工编号"	INTEGER NOT NULL,
	"毕业学校"	TEXT,
	"毕业日期"	TEXT,
	"学历"	TEXT,
	"专业"	TEXT,
	"外语"	TEXT,
	PRIMARY KEY("员工编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "员工录用信息表";
CREATE TABLE IF NOT EXISTS "员工录用信息表" (
	"签约合同号"	TEXT NOT NULL,
	"员工编号"	TEXT NOT NULL,
	"姓名"	TEXT NOT NULL,
	"签约日期"	TEXT NOT NULL,
	"到期日"	TEXT NOT NULL,
	"合同类型"	TEXT NOT NULL,
	"受聘部门"	TEXT NOT NULL,
	"受聘职务"	TEXT NOT NULL,
	"聘用标志"	TEXT NOT NULL,
	"备注"	TEXT,
	PRIMARY KEY("签约合同号"),
	FOREIGN KEY("员工编号") REFERENCES "员工基本信息表"("员工编号")
);
DROP TABLE IF EXISTS "员工私人信息表";
CREATE TABLE IF NOT EXISTS "员工私人信息表" (
	"员工编号"	TEXT NOT NULL,
	"姓名"	TEXT NOT NULL,
	"地址"	TEXT,
	"电话"	TEXT,
	"邮箱"	TEXT,
	"出生年月"	TEXT,
	"籍贯"	TEXT,
	"民族"	TEXT,
	"身份证号"	TEXT NOT NULL,
	"政治面貌"	TEXT,
	PRIMARY KEY("员工编号"),
	FOREIGN KEY("员工编号") REFERENCES "员工基本信息表"("员工编号")
);
DROP TABLE IF EXISTS "家庭关系表";
CREATE TABLE IF NOT EXISTS "家庭关系表" (
	"员工编号"	TEXT NOT NULL,
	"家庭编号"	TEXT NOT NULL,
	"姓名"	VARCHAR NOT NULL,
	"性别"	TEXT,
	"年龄"	INTEGER,
	"家属关系"	VARCHAR,
	"工作单位"	VARCHAR,
	PRIMARY KEY("员工编号"),
	FOREIGN KEY("员工编号") REFERENCES "员工基本信息表"("员工编号")
);
DROP TABLE IF EXISTS "工作考核信息表";
CREATE TABLE IF NOT EXISTS "工作考核信息表" (
	"员工编号"	TEXT NOT NULL,
	"考核日期"	TEXT NOT NULL,
	"工作态度"	TEXT,
	"工作业绩"	TEXT,
	"业务水平"	TEXT,
	"考核结论"	TEXT,
	"备注"	TEXT,
	PRIMARY KEY("员工编号"),
	FOREIGN KEY("员工编号") REFERENCES "员工基本信息表"("员工编号")
);
DROP TABLE IF EXISTS "工资标准信息表";
CREATE TABLE IF NOT EXISTS "工资标准信息表" (
	"工资等级编号"	INTEGER NOT NULL,
	"等级名称"	TEXT NOT NULL,
	"底薪"	REAL NOT NULL,
	"补贴"	REAL,
	"奖金"	REAL,
	"车补"	REAL,
	"房补"	REAL,
	"养老保险"	REAL,
	"医疗保险"	REAL,
	"住房公积金"	REAL,
	PRIMARY KEY("工资等级编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "工资计发信息表";
CREATE TABLE IF NOT EXISTS "工资计发信息表" (
	"自动编号"	INTEGER NOT NULL,
	"员工编号"	TEXT NOT NULL,
	"工资等级编号"	TEXT NOT NULL,
	"底薪"	REAL NOT NULL,
	"补贴"	REAL,
	"奖金"	REAL,
	"车补"	REAL,
	"房补"	REAL,
	"扣考核"	REAL,
	"加班费"	REAL,
	"代扣养老保险"	REAL,
	"代扣医疗保险"	REAL,
	"代扣住房公积金"	REAL,
	"税前小计"	REAL,
	"税率"	REAL,
	"应发工资"	REAL,
	"计发日期"	TEXT NOT NULL,
	PRIMARY KEY("自动编号" AUTOINCREMENT),
	FOREIGN KEY("员工编号") REFERENCES "员工基本信息表"("员工编号"),
	FOREIGN KEY("工资等级编号") REFERENCES "工资标准信息表"("工资等级编号")
);
DROP TABLE IF EXISTS "用户信息表";
CREATE TABLE IF NOT EXISTS "用户信息表" (
	"用户编号"	TEXT NOT NULL,
	"真实姓名"	TEXT NOT NULL,
	"用户类型"	TEXT DEFAULT 普通用户,
	"权限"	TEXT DEFAULT 10,
	"身份证号"	TEXT,
	"住址"	TEXT,
	"电话"	TEXT,
	"邮箱"	TEXT,
	PRIMARY KEY("用户编号"),
	FOREIGN KEY("用户编号") REFERENCES "用户验证表"("用户编号")
);
DROP TABLE IF EXISTS "用户验证表";
CREATE TABLE IF NOT EXISTS "用户验证表" (
	"用户编号"	INTEGER NOT NULL,
	"用户名"	TEXT NOT NULL UNIQUE,
	"密码"	TEXT,
	PRIMARY KEY("用户编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "考勤信息表";
CREATE TABLE IF NOT EXISTS "考勤信息表" (
	"自动编号"	INTEGER NOT NULL,
	"员工编号"	TEXT NOT NULL,
	"考勤日期"	TEXT NOT NULL,
	"考勤类型"	TEXT NOT NULL,
	"考勤天数"	TEXT NOT NULL,
	"备注"	TEXT NOT NULL,
	PRIMARY KEY("自动编号" AUTOINCREMENT),
	FOREIGN KEY("员工编号") REFERENCES "员工基本信息表"("员工编号")
);
DROP TABLE IF EXISTS "考勤考核信息表";
CREATE TABLE IF NOT EXISTS "考勤考核信息表" (
	"自动编号"	INTEGER NOT NULL,
	"员工编号"	TEXT NOT NULL,
	"出勤日期"	TEXT NOT NULL,
	"奖励"	TEXT NOT NULL,
	"惩罚"	TEXT NOT NULL,
	"加班费"	REAL NOT NULL,
	"扣考核"	REAL,
	PRIMARY KEY("自动编号" AUTOINCREMENT),
	FOREIGN KEY("员工编号") REFERENCES "员工基本信息表"("员工编号")
);
DROP TABLE IF EXISTS "职务信息表";
CREATE TABLE IF NOT EXISTS "职务信息表" (
	"职务代码"	TEXT NOT NULL,
	"职务名称"	TEXT NOT NULL,
	"工资等级"	TEXT NOT NULL,
	"工资上限"	REAL NOT NULL,
	"工资下限"	REAL NOT NULL,
	"简介"	TEXT,
	PRIMARY KEY("职务代码")
);
DROP TABLE IF EXISTS "部门信息表";
CREATE TABLE IF NOT EXISTS "部门信息表" (
	"部门代码"	TEXT NOT NULL,
	"部门名称"	TEXT NOT NULL,
	"领导姓名"	TEXT NOT NULL,
	"住址"	TEXT,
	"电话"	TEXT,
	"简介"	TEXT NOT NULL,
	PRIMARY KEY("部门代码")
);
DROP TRIGGER IF EXISTS "删除用户触发器";
CREATE TRIGGER 删除用户触发器 AFTER DELETE 
ON 用户信息表
BEGIN
    DELETE FROM 用户验证表 WHERE 用户编号 = old.用户编号;
END;
COMMIT;
