from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.sys_department import SysDepartment
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.api.deps import get_current_user
from app.models.sys_user import SysUser

router = APIRouter(prefix="/projects", tags=["项目管理"])


def _build_out(db: Session, p: Project, dept_map: dict | None = None) -> ProjectOut:
    sub_name = None
    if p.subsidiary_id:
        if dept_map and p.subsidiary_id in dept_map:
            sub_name = dept_map[p.subsidiary_id]
        else:
            d = db.get(SysDepartment, p.subsidiary_id)
            sub_name = d.name if d else None
    return ProjectOut(
        id=p.id, name=p.name, short_name=p.short_name, category=p.category,
        subsidiary_id=p.subsidiary_id, subsidiary_name=sub_name,
        address=p.address, status=p.status, created_at=p.created_at,
    )


@router.get("", response_model=list[ProjectOut])
def list_projects(
    keyword: str = "",
    category: str = "",
    status_filter: int | None = None,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    q = db.query(Project).filter(Project.is_deleted == 0)
    if keyword:
        q = q.filter(Project.name.contains(keyword))
    if category:
        q = q.filter(Project.category == category)
    if status_filter is not None:
        q = q.filter(Project.status == status_filter)
    rows = q.order_by(Project.id).all()

    dept_ids = list({r.subsidiary_id for r in rows if r.subsidiary_id})
    dept_map = {}
    if dept_ids:
        for d in db.query(SysDepartment).filter(SysDepartment.id.in_(dept_ids)).all():
            dept_map[d.id] = d.name
    return [_build_out(db, r, dept_map) for r in rows]

# ---------- 部门列表（下拉用） ----------
@router.get("/meta/departments")
def list_departments(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    """项目表单的"子分公司"下拉选项"""
    rows = (
        db.query(SysDepartment)
        .filter(SysDepartment.is_deleted == 0, SysDepartment.status == 1)
        .order_by(SysDepartment.sort_order)
        .all()
    )
    return [{"id": d.id, "name": d.name} for d in rows]


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    if db.query(Project).filter(Project.name == body.name, Project.is_deleted == 0).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "项目名称已存在")
    p = Project(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return _build_out(db, p)


@router.put("/{pid}", response_model=ProjectOut)
def update_project(
    pid: int,
    body: ProjectUpdate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    p = db.get(Project, pid)
    if not p or p.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "项目不存在")
    data = body.model_dump(exclude_none=True)
    if "name" in data:
        exists = db.query(Project).filter(
            Project.name == data["name"], Project.id != pid, Project.is_deleted == 0
        ).first()
        if exists:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "项目名称已存在")
    for k, v in data.items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return _build_out(db, p)


@router.delete("/{pid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    pid: int,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    p = db.get(Project, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "项目不存在")
    p.is_deleted = 1          #软删除
    db.commit()


@router.patch("/{pid}/status", response_model=ProjectOut)
def toggle_status(
    pid: int,
    body: dict,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    p = db.get(Project, pid)
    if not p or p.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "项目不存在")
    st = body.get("status")
    if st not in (0, 1):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "状态只能是 0/1")
    p.status = st
    db.commit()
    db.refresh(p)
    return _build_out(db, p)