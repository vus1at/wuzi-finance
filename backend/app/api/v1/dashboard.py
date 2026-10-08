from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ledger import Ledger
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["看板统计"])


@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """看板总览：KPI + 债务饼图 + TOP5 + 预警 + 概览（一次返回）"""

    # ---------- 1. KPI（全局 SUM） ----------
    row = db.query(
        func.coalesce(func.sum(Ledger.month_purchase_amt), 0).label("purchase"),
        func.coalesce(func.sum(Ledger.month_supply_amt), 0).label("supply"),
        func.coalesce(func.sum(Ledger.total_debt), 0).label("debt"),
        func.coalesce(func.sum(Ledger.receivable), 0).label("receivable"),
        func.coalesce(func.sum(Ledger.month_receive), 0).label("receive"),
        func.coalesce(func.sum(Ledger.month_profit), 0).label("profit"),
        func.coalesce(func.sum(Ledger.overdue_debt), 0).label("overdue_debt"),
        func.coalesce(func.sum(Ledger.overdue_receivable), 0).label("overdue_recv"),
    ).one()

    purchase = float(row.purchase)
    supply = float(row.supply)
    debt = float(row.debt)
    receivable = float(row.receivable)
    receive = float(row.receive)
    profit = float(row.profit)
    overdue_debt = float(row.overdue_debt)
    overdue_recv = float(row.overdue_recv)

    kpi = {
        "month_purchase": round(purchase, 2),
        "month_supply": round(supply, 2),
        "total_debt": round(debt, 2),
        "receivable": round(receivable, 2),
        "month_receive": round(receive, 2),
        # 派生指标
        "overdue_rate": round(overdue_debt / debt * 100, 2) if debt else 0,
        "recv_overdue_rate": round(overdue_recv / receivable * 100, 2) if receivable else 0,
        "receive_rate": round(receive / purchase * 100, 2) if purchase else 0,
    }

    # ---------- 2. 债务分级饼图（按 debt_level 分组） ----------
    pie_rows = db.query(
        Ledger.debt_level,
        func.sum(Ledger.total_debt).label("amount"),
    ).group_by(Ledger.debt_level).all()

    debt_pie = [
        {"name": r.debt_level or "未分级", "value": round(float(r.amount or 0), 2)}
        for r in pie_rows
    ]

    # ---------- 3. 项目供应 TOP5 ----------
    proj_rows = db.query(
        Ledger.project_name,
        func.sum(Ledger.month_supply_amt).label("amount"),
        func.group_concat(func.distinct(Ledger.material_type)).label("materials"),
    ).group_by(Ledger.project_name).order_by(func.sum(Ledger.month_supply_amt).desc()).limit(5).all()

    top_projects = []
    for r in proj_rows:
        mats = (r.materials or "").split(",")
        top_projects.append({
            "name": r.project_name,
            "value": round(float(r.amount or 0), 2),
            "material": mats[0] if mats else "",
        })

    # ---------- 4. 供应商债务 TOP5 ----------
    sup_rows = db.query(
        Ledger.supplier_name,
        func.sum(Ledger.total_debt).label("amount"),
    ).group_by(Ledger.supplier_name).order_by(func.sum(Ledger.total_debt).desc()).limit(5).all()

    top_suppliers = [
        {
            "name": r.supplier_name,
            "value": round(float(r.amount or 0), 2),
            "pct": round(float(r.amount or 0) / debt * 100, 2) if debt else 0,
        }
        for r in sup_rows
    ]

    # ---------- 5. 逾期预警列表（overdue_debt > 0） ----------
    alert_rows = db.query(Ledger).filter(Ledger.overdue_debt > 0).order_by(Ledger.overdue_debt.desc()).all()

    alerts = [
        {
            "supplier": r.supplier_name,
            "project": r.project_name,
            "value": round(float(r.overdue_debt), 2),
            "days": r.max_overdue_days,
        }
        for r in alert_rows
    ]

    # ---------- 6. 本月数据概览 ----------
    proj_cnt = db.query(func.count(func.distinct(Ledger.project_name))).scalar() or 0
    sup_cnt = db.query(func.count(func.distinct(Ledger.supplier_name))).scalar() or 0

    region_supply = db.query(func.coalesce(func.sum(Ledger.month_supply_amt), 0)).filter(
        Ledger.project_name.in_(["成达万", "中吉乌", "侨城东路", "西十2标"])
    ).scalar() or 0

    inner_supply = db.query(func.coalesce(func.sum(Ledger.month_supply_amt), 0)).filter(
        Ledger.project_name.in_(["大瑞1", "大瑞3", "大瑞4", "宜兴", "西丽"])
    ).scalar() or 0

    high_risk_debt = db.query(func.coalesce(func.sum(Ledger.total_debt), 0)).filter(
        Ledger.debt_level == "高风险"
    ).scalar() or 0

    overview = {
        "project_count": proj_cnt,
        "supplier_count": sup_cnt,
        "region_supply": round(float(region_supply), 2),
        "inner_supply": round(float(inner_supply), 2),
        "high_risk_debt": round(float(high_risk_debt), 2),
        "total_profit": round(profit, 2),
        "total_overdue_debt": round(overdue_debt, 2),
        "total_overdue_recv": round(overdue_recv, 2),
    }

    return {
        "kpi": kpi,
        "debt_pie": debt_pie,
        "top_projects": top_projects,
        "top_suppliers": top_suppliers,
        "alerts": alerts,
        "overview": overview,
    }