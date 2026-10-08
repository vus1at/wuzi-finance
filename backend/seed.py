from app.db.session import SessionLocal, Base, engine
from app.models.user import User
from app.models.project import Project
from app.models.supplier import Supplier
from app.models.ledger import Ledger
from app.core.security import hash_password
from app.models.dict_item import DictItem
from app.core.dicts import DICT_META

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    # 1. 创建 admin 账号
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(
            username="admin",
            password=hash_password("123456"),
            real_name="管理员",
            dept="财务部",
            role="admin",
            data_scope="all",
        ))
        db.commit()
        print("[OK] 已创建账号 admin / 123456")
    else:
        print("[INFO] admin 已存在，跳过")

    # 2. 创建项目数据
    PROJECTS = [
        {"name": "大瑞1",     "category": "铁路", "sub_company": "一处", "addr": "云南大理"},
        {"name": "大瑞3",     "category": "铁路", "sub_company": "一处", "addr": "云南大理"},
        {"name": "大瑞4",     "category": "铁路", "sub_company": "一处", "addr": "云南大理"},
        {"name": "成达万",    "category": "铁路", "sub_company": "一处", "addr": "四川成都"},
        {"name": "宜兴",      "category": "市政", "sub_company": "二处", "addr": "江苏宜兴"},
        {"name": "西十2标",   "category": "铁路", "sub_company": "三处", "addr": "陕西西安"},
        {"name": "侨城东路",  "category": "市政", "sub_company": "四处", "addr": "广东深圳"},
        {"name": "西丽",      "category": "市政", "sub_company": "四处", "addr": "广东深圳", "status": "停用"},
        {"name": "中吉乌",    "category": "铁路", "sub_company": "五处", "addr": "新疆喀什"},
    ]
    added = 0
    for p in PROJECTS:
        if not db.query(Project).filter(Project.name == p["name"]).first():
            db.add(Project(**p))
            added += 1
    db.commit()
    print(f"[OK] 已添加 {added} 个项目")

    # 3. 创建供应商数据
    SUPPLIERS = [
        {"name": "泰安现代塑料有限公司",     "type": "厂商", "contact": "张伟", "phone": "138-0538-0001", "addr": "山东省泰安市高新区工业园", "scope": "土工合成材料、塑料制品生产销售", "capital": "8000万", "founded": "2003-06-20"},
        {"name": "物产中大金属集团有限公司", "type": "厂商", "contact": "李明", "phone": "0571-8888-8888", "addr": "浙江省杭州市拱墅区",     "scope": "金属材料、钢材及制品贸易",       "capital": "50亿",   "founded": "1992-12-08"},
        {"name": "山东龙泉管道工程股份有限公司", "type": "厂商", "contact": "王强", "phone": "0634-6666-6666", "addr": "山东省淄博市博山区", "scope": "钢管、波纹管制造销售",       "capital": "3.2亿",  "founded": "2001-05-15"},
        {"name": "海螺水泥股份有限公司",     "type": "厂商", "contact": "陈静", "phone": "0553-9999-9999", "addr": "安徽省芜湖市镜湖区",     "scope": "水泥及熟料生产销售",           "capital": "50亿",   "founded": "1997-09-01"},
        {"name": "云南建投混凝土公司",       "type": "厂商", "contact": "赵敏", "phone": "0871-7777-7777", "addr": "云南省昆明市官渡区",     "scope": "商品混凝土生产供应",           "capital": "2亿",    "founded": "2008-03-12"},
        {"name": "陕西钢铁集团有限公司",     "type": "厂商", "contact": "刘洋", "phone": "0917-8888-8888", "addr": "陕西省宝鸡市高新区",     "scope": "钢材、钢绞线生产销售",         "capital": "20亿",   "founded": "2000-11-01"},
        {"name": "四川金阳外加剂有限公司",   "type": "厂商", "contact": "孙鹏", "phone": "028-5555-5555", "addr": "四川省成都市温江区",     "scope": "混凝土外加剂研发生产",         "capital": "5000万", "founded": "2010-07-08"},
        {"name": "天津银龙预应力材料公司",   "type": "厂商", "contact": "周杰", "phone": "022-6666-6666", "addr": "天津市西青区",           "scope": "预应力钢绞线、锚具制造",       "capital": "1.5亿",  "founded": "2005-04-20"},
    ]
    added_s = 0
    for s in SUPPLIERS:
        if not db.query(Supplier).filter(Supplier.name == s["name"]).first():
            db.add(Supplier(**s))
            added_s += 1
    db.commit()
    print(f"[OK] 已添加 {added_s} 个供应商")

    # 4. 创建台账数据（跟原型里的 10 条一致）
    LEDGERS = [
        # 项目,         供应商,                物资,       采购,  供应,  利润, 支付, 回款, 债务,    逾期,   天数, 应收, 逾期债权, 分级
        ("大瑞1",     "泰安现代塑料有限公司",   "土工布",    33,    34,    20,    0,    0,   46.28,  0,    187,   0,    0,     "高风险"),
        ("大瑞1",     "泰安现代塑料有限公司",   "木材",      33,    34,    0,     0,    0,   88.49,  88.49,187,   0,    0,     "高风险"),
        ("大瑞3",     "泰安现代塑料有限公司",   "波纹管",    33,    34,    0,     0,    0,   5.74,   0,    62,    0,    0,     "中风险"),
        ("大瑞4",     "泰安现代塑料有限公司",   "预埋槽道",  33,    34,    0,     0,    0,   28.65,  0,    95,    0,    0,     "中风险"),
        ("成达万",    "物产中大金属集团有限公司","型材",      180,   168,   18,    80,   0,   168,    0,    0,     96,   0,     "战略"),
        ("中吉乌",    "海螺水泥股份有限公司",   "水泥",      96,    90,    9,     90,   0,   90,     0,    0,     88,   0,     "战略"),
        ("宜兴",      "四川金阳外加剂有限公司", "外加剂",    18.6,  17.5,  2,     0,    0,   18.6,   0,    0,     72,   0,     "中风险"),
        ("侨城东路",  "云南建投混凝土公司",     "商砼",      45,    42,    4.5,   22,   0,   42,     12,   45,    58,   12,    "低风险"),
        ("西十2标",   "陕西钢铁集团有限公司",   "钢绞线",    72.4,  66,    7,     0,    0,   66,     0,    0,     95,   0,     "低风险"),
        ("西丽",      "泰安现代塑料有限公司",   "土工布",    28,    26,    0,     0,    0,   28,     28,   120,   120,  35,    "高风险"),
    ]
    added_l = 0
    for (proj, sup, mat, cg, gy, lr, pay, recv, debt, overdue, days, ys, yq_credit, fx) in LEDGERS:
        if not db.query(Ledger).filter(
            Ledger.project_name == proj,
            Ledger.supplier_name == sup,
            Ledger.material_type == mat,
        ).first():
            db.add(Ledger(
                project_name=proj,
                supplier_name=sup,
                material_type=mat,
                month_purchase_amt=cg,
                month_supply_amt=gy,
                month_profit=lr,
                month_pay=pay,
                month_receive=recv,
                total_debt=debt,
                overdue_debt=overdue,
                max_overdue_days=days,
                receivable=ys,
                overdue_receivable=yq_credit,
                debt_level=fx,
            ))
            added_l += 1
    db.commit()
    print(f"[OK] 已添加 {added_l} 条台账")

    # 5. 初始化字典选项
    added_d = 0
    for meta in DICT_META:
        # 该字典如果已有数据就跳过
        exist = db.query(DictItem).filter(DictItem.dict_key == meta["key"]).first()
        if exist:
            continue
        for i, v in enumerate(meta["items"]):
            db.add(DictItem(dict_key=meta["key"], dict_value=v, sort_order=i))
            added_d += 1
    db.commit()
    print(f"[OK] 已初始化 {added_d} 个字典选项")

finally:
    db.close()