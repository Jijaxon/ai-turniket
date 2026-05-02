"""
Access log routes: query, filter, export.
"""

import io
import csv
from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, distinct

from app.core.security import get_current_admin
from app.database.db import get_db
from app.database.models import AccessLog, User
from app.schemas.log import LogList, AccessLogResponse, StatsResponse, DailyStats

router = APIRouter(prefix="/logs", tags=["Access Logs"])


def _log_to_schema(log: AccessLog) -> AccessLogResponse:
    return AccessLogResponse(
        id=log.id,
        user_id=log.user_id,
        user_name=log.user.name if log.user else None,
        timestamp=log.timestamp,
        status=log.status,
        confidence=log.confidence,
        reason=log.reason,
        ip_address=log.ip_address,
    )


@router.get("/", response_model=LogList, summary="List all access logs")
def get_logs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, regex="^(allowed|denied)$"),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    query = db.query(AccessLog).options(joinedload(AccessLog.user))
    if status:
        query = query.filter(AccessLog.status == status)
    total = query.count()
    logs = query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()
    return LogList(total=total, logs=[_log_to_schema(l) for l in logs])


@router.get("/today", response_model=LogList, summary="Today's access logs")
def get_today_logs(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    today_start = datetime.combine(date.today(), datetime.min.time())
    logs = (
        db.query(AccessLog)
        .options(joinedload(AccessLog.user))
        .filter(AccessLog.timestamp >= today_start)
        .order_by(AccessLog.timestamp.desc())
        .all()
    )
    return LogList(total=len(logs), logs=[_log_to_schema(l) for l in logs])


@router.get("/stats", response_model=StatsResponse, summary="Dashboard statistics")
def get_stats(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    today_start = datetime.combine(date.today(), datetime.min.time())

    # Today's stats
    today_query = db.query(AccessLog).filter(AccessLog.timestamp >= today_start)
    today_total = today_query.count()
    today_allowed = today_query.filter(AccessLog.status == "allowed").count()
    today_denied = today_total - today_allowed
    today_unique = db.query(func.count(distinct(AccessLog.user_id))).filter(
        AccessLog.timestamp >= today_start,
        AccessLog.user_id.isnot(None),
    ).scalar() or 0

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_logs = db.query(func.count(AccessLog.id)).scalar() or 0

    recent = (
        db.query(AccessLog)
        .options(joinedload(AccessLog.user))
        .order_by(AccessLog.timestamp.desc())
        .limit(10)
        .all()
    )

    return StatsResponse(
        today=DailyStats(
            date=date.today().isoformat(),
            total=today_total,
            allowed=today_allowed,
            denied=today_denied,
            unique_users=today_unique,
        ),
        total_users=total_users,
        total_logs=total_logs,
        recent_logs=[_log_to_schema(l) for l in recent],
    )


@router.get("/daily-report", summary="Last 7 days daily breakdown")
def daily_report(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Returns day-by-day allowed/denied counts for the last 7 days."""
    report = []
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        start = datetime.combine(day, datetime.min.time())
        end = datetime.combine(day, datetime.max.time())
        total = db.query(AccessLog).filter(AccessLog.timestamp.between(start, end)).count()
        allowed = (
            db.query(AccessLog)
            .filter(AccessLog.timestamp.between(start, end), AccessLog.status == "allowed")
            .count()
        )
        report.append({
            "date": day.isoformat(),
            "total": total,
            "allowed": allowed,
            "denied": total - allowed,
        })
    return report


@router.get("/export/csv", summary="Export logs as CSV")
def export_csv(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Download all access logs as a CSV file."""
    logs = (
        db.query(AccessLog)
        .options(joinedload(AccessLog.user))
        .order_by(AccessLog.timestamp.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "timestamp", "user_id", "user_name", "status", "confidence", "reason", "ip_address"])
    for log in logs:
        writer.writerow([
            log.id,
            log.timestamp.isoformat(),
            log.user_id,
            log.user.name if log.user else "Unknown",
            log.status,
            log.confidence,
            log.reason,
            log.ip_address,
        ])

    output.seek(0)
    filename = f"access_logs_{date.today().isoformat()}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
