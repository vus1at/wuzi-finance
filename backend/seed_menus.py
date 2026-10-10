"""初始化菜单数据"""
from app.db.session import SessionLocal
from app.models.sys_menu import SysMenu

# (parent_id, menu_name, menu_code, path, component, icon, menu_type, sort_order)
MENUS = [
    # ---------- 顶级 ----------
    (0, "看板统计",   "dashboard",    "/dashboard",       "views/dashboard/index",  "Odometer",          1, 1),
    (0, "数据填报",   "input",        "/input",           "views/placeholder",      "Upload",            1, 2),
    (0, "报表中心",   "report",       "/report",          "views/placeholder",      "PieChart",          1, 3),
    (0, "债务概况",   "debt",         "/debt",            "views/placeholder",      "Tickets",           1, 4),
    (0, "债权概况",   "credit",       "/credit",          "views/placeholder",      "ScaleToOriginal",   1, 5),
    (0, "系统管理",   "system",       "",                 "",                       "Setting",           2, 6),
]

# 系统管理下的子菜单，parent_id=6（假设"系统管理"id 是 6）
SUB_MENUS = [
    ("项目管理",     "projects",     "/system/projects",  "views/system/projects",  "OfficeBuilding", 3, 1),
    ("供应商管理",   "suppliers",    "/system/suppliers", "views/system/suppliers", "Connection",     3, 2),
    ("字典管理",     "dicts",        "/system/dicts",     "views/system/dicts",     "List",           3, 3),
    ("用户权限",     "users",        "/system/users",     "views/system/users",     "UserFilled",     3, 4),
    ("期初初始化",   "init",         "/system/init",      "views/placeholder",      "Upload",         3, 5),
    ("菜单管理",     "menus",        "/system/menus",     "views/system/menus",     "Menu",           3, 6),
]

db = SessionLocal()
try:
    # 顶层
    for (pid, name, code, path, comp, icon, mtype, sort) in MENUS:
        if not db.query(SysMenu).filter(SysMenu.menu_code == code).first():
            db.add(SysMenu(
                parent_id=pid, menu_name=name, menu_code=code,
                path=path, component=comp, icon=icon,
                menu_type=mtype, sort_order=sort,
            ))
    db.commit()

    # 取"系统管理"的 id
    sys_parent = db.query(SysMenu).filter(SysMenu.menu_code == "system").first()
    if sys_parent:
        for (name, code, path, comp, icon, mtype, sort) in SUB_MENUS:
            if not db.query(SysMenu).filter(SysMenu.menu_code == code).first():
                db.add(SysMenu(
                    parent_id=sys_parent.id, menu_name=name, menu_code=code,
                    path=path, component=comp, icon=icon,
                    menu_type=mtype, sort_order=sort,
                ))
        db.commit()

    total = db.query(SysMenu).filter(SysMenu.is_deleted == 0).count()
    print(f"[OK] 菜单共 {total} 条")
finally:
    db.close()