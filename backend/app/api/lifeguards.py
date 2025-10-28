from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from ..core.deps import get_session
from ..models.lifeguard import Lifeguard
from ..schemas.lifeguard import LifeguardCreate, LifeguardRead, LifeguardUpdate
from ..services.import_export import export_lifeguards_to_csv, load_lifeguards_from_csv

router = APIRouter(prefix="/lifeguards", tags=["lifeguards"])


@router.get("", response_model=list[LifeguardRead])
def list_lifeguards(present: bool | None = None, q: str | None = None, session: Session = Depends(get_session)):
    statement = select(Lifeguard)
    if present is not None:
        statement = statement.where(Lifeguard.present == present)
    if q:
        statement = statement.where(Lifeguard.name.contains(q))
    return session.exec(statement).all()


@router.post("", response_model=LifeguardRead)
def create_lifeguard(payload: LifeguardCreate, session: Session = Depends(get_session)):
    guard = Lifeguard(**payload.dict())
    session.add(guard)
    session.commit()
    session.refresh(guard)
    return guard


@router.put("/{guard_id}", response_model=LifeguardRead)
def update_lifeguard(guard_id: int, payload: LifeguardUpdate, session: Session = Depends(get_session)):
    guard = session.get(Lifeguard, guard_id)
    if not guard:
        raise HTTPException(status_code=404, detail="Guard not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(guard, key, value)
    session.add(guard)
    session.commit()
    session.refresh(guard)
    return guard


@router.delete("/{guard_id}")
def delete_lifeguard(guard_id: int, session: Session = Depends(get_session)):
    guard = session.get(Lifeguard, guard_id)
    if not guard:
        raise HTTPException(status_code=404, detail="Guard not found")
    session.delete(guard)
    session.commit()
    return {"ok": True}


@router.post("/import")
def import_lifeguards(file: UploadFile, session: Session = Depends(get_session)):
    load_lifeguards_from_csv(file, session)
    return {"ok": True}


@router.get("/export")
def export_lifeguards(session: Session = Depends(get_session)):
    csv_bytes = export_lifeguards_to_csv(session)
    return StreamingResponse(iter([csv_bytes]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=lifeguards.csv"})
