"""把旧t_user表的用户迁到新sys_user表，并建3个角色"""
from app.db.session import SessionLocal
from app.models.sys_user import SysUser
from app.models.sys_role import SysRole
from app.models.sys_user_role import SysUserRole
from app.models.user import User as OldUser   # 旧表

db = SessionLocal()
try:
    # 1. 建 3 个角色
    roles = [
        {"role_name": "管理员", "role_code": "ADMIN", "description": "系统管理员，全部权限"},
        {"role_name": "填报人", "role_code": "EDITOR", "description": "数据填报人员"},
        {"role_name": "查看人", "role_code": "VIEWER", "description": "只能查看报表"},
    ]
    for r in roles:
        if not db.query(SysRole).filter(SysRole.role_code == r["role_code"]).first():
            db.add(SysRole(**r))
    db.commit()
    print("[OK] 角色已创建（ADMIN / EDITOR / VIEWER）")

    # 2. 迁移旧用户
    old_users = db.query(OldUser).all()
    role_map = {"admin": "ADMIN", "editor": "EDITOR", "viewer": "VIEWER"}
    migrated = 0
    for ou in old_users:
        if db.query(SysUser).filter(SysUser.username == ou.username).first():
            continue
        new_u = SysUser(
            username=ou.username,
            password=ou.password,
            real_name=ou.real_name,
            status=1 if ou.status == "enabled" else 0,
        )
        db.add(new_u)
        db.flush()   # 拿到 new_u.id

        role_code = role_map.get(ou.role, "VIEWER")
        role = db.query(SysRole).filter(SysRole.role_code == role_code).first()
        if role:
            db.add(SysUserRole(user_id=new_u.id, role_id=role.id))
        migrated += 1
    db.commit()
    print(f"[OK] 迁移了 {migrated} 个用户")

    # 3. 统计
    total_u = db.query(SysUser).count()
    total_r = db.query(SysRole).count()
    total_ur = db.query(SysUserRole).count()
    print(f"[STAT] sys_user={total_u}, sys_role={total_r}, sys_user_role={total_ur}")
finally:
    db.close()