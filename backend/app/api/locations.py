from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from ..core.deps import get_session
from ..models.location import Location
from ..schemas.location import LocationCreate, LocationRead, LocationUpdate
from ..services.import_export import export_locations_to_csv, load_locations_from_csv

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationRead])
def list_locations(active_today: bool | None = None, session: Session = Depends(get_session)):
    statement = select(Location)
    if active_today is not None:
        statement = statement.where(Location.active_today == active_today)
    return session.exec(statement).all()


@router.post("", response_model=LocationRead)
def create_location(payload: LocationCreate, session: Session = Depends(get_session)):
    location = Location(**payload.dict())
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@router.put("/{location_id}", response_model=LocationRead)
def update_location(location_id: int, payload: LocationUpdate, session: Session = Depends(get_session)):
    location = session.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(location, key, value)
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@router.delete("/{location_id}")
def delete_location(location_id: int, session: Session = Depends(get_session)):
    location = session.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    session.delete(location)
    session.commit()
    return {"ok": True}


@router.post("/import")
def import_locations(file: UploadFile, session: Session = Depends(get_session)):
    load_locations_from_csv(file, session)
    return {"ok": True}


@router.get("/export")
def export_locations(session: Session = Depends(get_session)):
    csv_bytes = export_locations_to_csv(session)
    return StreamingResponse(iter([csv_bytes]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=locations.csv"})
