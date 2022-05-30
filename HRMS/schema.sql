BEGIN TRANSACTION;
DROP TABLE IF EXISTS "员工基本信息表";
CREATE TABLE IF NOT EXISTS "员工基本信息表" (
	"员工编号"	INTEGER NOT NULL,
	"姓名"	TEXT NOT NULL,
	"性别"	TEXT NOT NULL,
	"出生年月"	TEXT,
	"籍贯"	TEXT,
	"民族"	TEXT,
	"身份证号"	TEXT NOT NULL,
	"政治面貌"	TEXT,
	"所属部门编号"	TEXT,
	"进入部门日期"	TEXT NOT NULL,
	"职务代码"	TEXT NOT NULL,
	"职称"	TEXT,
	"起薪日"	TEXT,
	"原单位"	TEXT,
	"原职称"	TEXT,
	"原职务"	TEXT,
	"毕业学校"	TEXT,
	"毕业日期"	TEXT,
	"学历"	TEXT,
	"专业"	TEXT,
	"外语"	TEXT,
	"地址"	TEXT,
	"电话"	TEXT,
	"邮箱"	TEXT,
	"在岗状态"	TEXT NOT NULL,
	PRIMARY KEY("员工编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "员工录用信息表";
CREATE TABLE IF NOT EXISTS "员工录用信息表" (
	"签约合同号"	INTEGER NOT NULL,
	"员工编号"	TEXT NOT NULL,
	"姓名"	TEXT NOT NULL,
	"签约日期"	TEXT NOT NULL,
	"到期日"	TEXT NOT NULL,
	"合同类型"	TEXT NOT NULL,
	"受聘部门"	TEXT NOT NULL,
	"受聘职务"	TEXT NOT NULL,
	"聘用标志"	TEXT NOT NULL,
	"备注"	TEXT,
	PRIMARY KEY("签约合同号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "工作考核信息表";
CREATE TABLE IF NOT EXISTS "工作考核信息表" (
	"员工编号"	INTEGER NOT NULL,
	"考核日期"	TEXT NOT NULL,
	"工作态度"	TEXT,
	"工作业绩"	TEXT,
	"业务水平"	TEXT,
	"考核结论"	TEXT,
	"备注"	TEXT,
	PRIMARY KEY("员工编号" AUTOINCREMENT)
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
	PRIMARY KEY("自动编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "用户信息表";
CREATE TABLE IF NOT EXISTS "用户信息表" (
	"用户编号"	TEXT NOT NULL,
	"用户类型"	TEXT,
	"权限"	TEXT,
	"身份证号"	TEXT,
	"住址"	TEXT,
	"电话"	TEXT,
	"邮箱"	TEXT
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
	PRIMARY KEY("自动编号" AUTOINCREMENT)
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
	PRIMARY KEY("自动编号" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "职务信息表";
CREATE TABLE IF NOT EXISTS "职务信息表" (
	"职务代码"	INTEGER NOT NULL,
	"职务名称"	TEXT NOT NULL,
	"工资等级"	TEXT NOT NULL,
	"工资上限"	REAL NOT NULL,
	"工资下限"	REAL NOT NULL,
	"简介"	TEXT,
	PRIMARY KEY("职务代码" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "部门信息表";
CREATE TABLE IF NOT EXISTS "部门信息表" (
	"部门代码"	INTEGER NOT NULL,
	"部门名称"	TEXT NOT NULL,
	"领导姓名"	TEXT NOT NULL,
	"住址"	TEXT,
	"电话"	TEXT,
	"简介"	TEXT NOT NULL,
	PRIMARY KEY("部门代码" AUTOINCREMENT)
);
COMMIT;
