"""给 ADMIN 角色分配全部菜单（一次性）"""
from app.db.session import SessionLocal
from app.models.sys_role import SysRole
from app.models.sys_menu import SysMenu
from app.models.sys_role_menu import SysRoleMenu

db = SessionLocal()
try:
    admin_role = db.query(SysRole).filter(SysRole.role_code == "ADMIN").first()
    if not admin_role:
        print("[ERROR] ADMIN 角色不存在")
    else:
        # 清空再插
        db.query(SysRoleMenu).filter(SysRoleMenu.role_id == admin_role.id).delete()
        menus = db.query(SysMenu).filter(SysMenu.is_deleted == 0).all()
        for m in menus:
            db.add(SysRoleMenu(role_id=admin_role.id, menu_id=m.id))
        db.commit()
        print(f"[OK] ADMIN 角色已分配 {len(menus)} 个菜单")
finally:
    db.close()