# QXJH 数据中台（可用框架版）

这是一个基于 Flask + MySQL 的可用后台框架版本，用于后续承载多系统数据汇聚、整合与展示。

## 当前已包含（可操作）
- 登录认证
- 用户管理：新增、编辑、删除、列表
- 组织架构管理：新增、编辑、删除、列表
- 角色管理：新增、编辑、删除、列表
- 权限管理：新增、编辑、删除、列表
- 人员分配部门
- 角色分配给人员
- 页面权限分配给角色（RBAC）
- 源数据表与最终结果表展示页

## 技术栈
- Flask
- Flask-SQLAlchemy
- Flask-Login
- MySQL（PyMySQL）

## 目录结构
```text
qxjh/
  app/
    auth/
    admin/
    dashboard/
    templates/
    static/
    models.py
    permissions.py
    config.py
  run.py
  requirements.txt
```

## 启动步骤（首次）
1. 进入目录
```bash
cd /Users/shaobin/Desktop/code/qxjh
```

2. 创建虚拟环境
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 初始化数据库表
```bash
flask --app run.py init-db
```

5. 写入演示数据
```bash
flask --app run.py seed-demo
```

6. 启动服务
```bash
flask --app run.py run --debug --host 127.0.0.1 --port 5001
```

## 默认账号
- 用户名：`admin`
- 密码：`admin123`

## 下一步可扩展
- 源数据表/结果表的增删改查
- 字段映射配置、数据清洗规则
- ETL/ELT 任务编排与运行日志
- 菜单级权限点与按钮级权限点
