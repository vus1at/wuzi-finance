"""迁移：
1. 建 11 个子分公司部门
2. t_project → project
3. t_supplier → supplier
"""
import re
from sqlalchemy import text
from app.db.session import SessionLocal
from app.models.sys_department import SysDepartment
from app.models.project import Project
from app.models.supplier import Supplier

DEPARTMENTS = ["一处", "二处", "三处", "四处", "五处", "六处",
               "隧道股份", "机电", "设备", "特种", "局外单位"]

db = SessionLocal()
try:
    # ---------- 1. 建部门 ----------
    name_to_id = {}
    for i, name in enumerate(DEPARTMENTS, 1):
        d = db.query(SysDepartment).filter(SysDepartment.name == name).first()
        if not d:
            d = SysDepartment(name=name, code=f"DEPT_{i:02d}", sort_order=i, level=1, path="0")
            db.add(d)
            db.flush()
        name_to_id[name] = d.id
    db.commit()
    print(f"[OK] 部门 {len(name_to_id)} 个")

    # ---------- 2. 迁移 t_project ----------
    old_projects = db.execute(text(
        "SELECT name, category, sub_company, addr, status FROM t_project"
    )).fetchall()
    p_migrated = 0
    for r in old_projects:
        if db.query(Project).filter(Project.name == r.name).first():
            continue
        db.add(Project(
            name=r.name,
            short_name=r.name,
            category=r.category,
            subsidiary_id=name_to_id.get(r.sub_company),
            address=r.addr,
            status=1 if r.status == "启用" else 0,
        ))
        p_migrated += 1
    db.commit()
    print(f"[OK] 项目迁移 {p_migrated} 条")

    # ---------- 3. 迁移 t_supplier ----------
    old_suppliers = db.execute(text(
        "SELECT name, type, contact, phone, addr, scope, capital, founded FROM t_supplier"
    )).fetchall()
    s_migrated = 0
    for r in old_suppliers:
        if db.query(Supplier).filter(Supplier.name == r.name).first():
            continue
        # "8000万" / "50亿" → Decimal
        amt = None
        if r.capital:
            m = re.match(r"([\d.]+)", str(r.capital))
            if m:
                num = float(m.group(1))
                if "亿" in str(r.capital):
                    num *= 10000
                amt = num
        db.add(Supplier(
            name=r.name,
            type=1 if r.type == "厂商" else 0,
            contact_name=r.contact,
            contact_mobile=r.phone,
            company_address=r.addr,
            business_scope=r.scope,
            amount=amt,
            established_date=r.founded if r.founded else None,
        ))
        s_migrated += 1
    db.commit()
    print(f"[OK] 供应商迁移 {s_migrated} 条")

    print(f"[STAT] project={db.query(Project).count()}, supplier={db.query(Supplier).count()}")
finally:
    db.close()