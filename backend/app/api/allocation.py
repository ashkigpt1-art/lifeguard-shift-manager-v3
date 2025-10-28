from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from ..core.deps import get_session
from ..models.shift_history import ShiftHistory
from ..schemas.history import AllocationResponse
from ..services.allocation_engine import AllocationEngine

router = APIRouter(prefix="/allocate", tags=["allocation"])


@router.post("", response_model=AllocationResponse)
def allocate(session: Session = Depends(get_session)):
    engine = AllocationEngine(session)
    result = engine.allocate()
    request_state["engine"] = engine
    return result


@router.get("/history")
def read_history(date: str | None = None, session: Session = Depends(get_session)):
    statement = select(ShiftHistory)
    if date:
        statement = statement.where(ShiftHistory.date_jalali == date)
    records = session.exec(statement).all()
    return [
        {
            "id": row.id,
            "date_jalali": row.date_jalali,
            "guard_name": row.guard_name,
            "location_name": row.location_name,
            "start": row.start,
            "end": row.end,
            "kind": row.kind,
            "created_at": row.created_at,
        }
        for row in records
    ]


request_state: dict[str, AllocationEngine] = {}


@router.get("/export/wide.csv")
def export_wide():
    engine = request_state.get("engine")
    if not engine:
        raise HTTPException(status_code=400, detail="No allocation run yet")
    csv_bytes = engine.export_wide_csv()
    return StreamingResponse(iter([csv_bytes]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=wide.csv"})


@router.get("/export/long.csv")
def export_long():
    engine = request_state.get("engine")
    if not engine:
        raise HTTPException(status_code=400, detail="No allocation run yet")
    csv_bytes = engine.export_long_csv()
    return StreamingResponse(iter([csv_bytes]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=long.csv"})
