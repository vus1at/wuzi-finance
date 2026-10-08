from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectStatusUpdate, ProjectOut
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.get("", response_model=list[ProjectOut])
def list_projects(
    keyword: str = "",
    category: str = "",
    status_filter: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    #项目列表
    q = db.query(Project)
    if keyword:
        q = q.filter(Project.name.contains(keyword))
    if category:
        q = q.filter(Project.category == category)
    if status_filter:
        q = q.filter(Project.status == status_filter)
    return q.order_by(Project.id).all()


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    #新增项目
    if db.query(Project).filter(Project.name == body.name).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "项目名称已存在")
    p = Project(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{pid}", response_model=ProjectOut)
def update_project(
    pid: int,
    body: ProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    #编辑项目
    p = db.get(Project, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "项目不存在")
    data = body.model_dump(exclude_none=True)
    if "name" in data:
        exists = db.query(Project).filter(
            Project.name == data["name"], Project.id != pid
        ).first()
        if exists:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "项目名称已存在")
    for k, v in data.items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{pid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    pid: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    #删除项目
    p = db.get(Project, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "项目不存在")
    db.delete(p)
    db.commit()


@router.patch("/{pid}/status", response_model=ProjectOut)
def toggle_status(
    pid: int,
    body: ProjectStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    #切换项目状态
    p = db.get(Project, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "项目不存在")
    if body.status not in ("启用", "停用"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "状态只能是启用/停用")
    p.status = body.status
    db.commit()
    db.refresh(p)
    return p