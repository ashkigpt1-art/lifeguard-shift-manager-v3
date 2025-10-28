from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from ..core.deps import get_session
from ..models.setting import Setting
from ..schemas.setting import SettingRead, SettingUpdate
from ..services.import_export import export_settings_to_yaml, load_settings_from_yaml

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingRead)
def get_settings(session: Session = Depends(get_session)):
    setting = session.get(Setting, 1)
    if not setting:
        raise HTTPException(status_code=404, detail="Settings not configured")
    return SettingRead(
        start=setting.start,
        end=setting.end,
        shift_hours=setting.shift_hours,
        special_hours=setting.special_hours,
        lunch_min=setting.lunch_min,
        dinner_min=setting.dinner_min,
        shower_min=setting.shower_min,
        max_concurrent_lunch=setting.max_concurrent_lunch,
        check_windows_min=setting.check_windows,
        check_window_len_min=setting.check_window_len_min,
    )


@router.put("", response_model=SettingRead)
def update_settings(payload: SettingUpdate, session: Session = Depends(get_session)):
    setting = session.get(Setting, 1)
    if not setting:
        setting = Setting(id=1)
    setting.start = payload.start
    setting.end = payload.end
    setting.shift_hours = payload.shift_hours
    setting.special_hours = payload.special_hours
    setting.lunch_min = payload.lunch_min
    setting.dinner_min = payload.dinner_min
    setting.shower_min = payload.shower_min
    setting.max_concurrent_lunch = payload.max_concurrent_lunch
    setting.check_windows_min = ",".join(str(x) for x in payload.check_windows_min)
    setting.check_window_len_min = payload.check_window_len_min
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return get_settings(session)


@router.post("/import")
def import_settings(file: UploadFile, session: Session = Depends(get_session)):
    load_settings_from_yaml(file, session)
    return {"ok": True}


@router.get("/export")
def export_settings(session: Session = Depends(get_session)):
    yaml_bytes = export_settings_to_yaml(session)
    return StreamingResponse(
        iter([yaml_bytes]),
        media_type="application/x-yaml",
        headers={"Content-Disposition": "attachment; filename=settings.yaml"},
    )
