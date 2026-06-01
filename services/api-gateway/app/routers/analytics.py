"""Analytics and reporting API endpoints."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from shared.db.database import get_db
from shared.db.models import Beat, Sale, RenderJob, Genre

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    """Get main dashboard metrics."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Total beats
    total_beats_result = await db.execute(select(func.count()).select_from(Beat))
    total_beats = total_beats_result.scalar() or 0

    # Beats today
    beats_today_result = await db.execute(
        select(func.count()).select_from(Beat).where(Beat.created_at >= today)
    )
    beats_today = beats_today_result.scalar() or 0

    # Beats this week
    beats_week_result = await db.execute(
        select(func.count()).select_from(Beat).where(Beat.created_at >= week_start)
    )
    beats_this_week = beats_week_result.scalar() or 0

    # Beats this month
    beats_month_result = await db.execute(
        select(func.count()).select_from(Beat).where(Beat.created_at >= month_start)
    )
    beats_this_month = beats_month_result.scalar() or 0

    # Average quality score
    avg_quality_result = await db.execute(
        select(func.avg(Beat.quality_score)).where(Beat.quality_score.isnot(None))
    )
    avg_quality = round(avg_quality_result.scalar() or 0, 2)

    # QC pass rate
    qc_total_result = await db.execute(
        select(func.count()).select_from(Beat).where(Beat.qc_passed.isnot(None))
    )
    qc_total = qc_total_result.scalar() or 0
    qc_passed_result = await db.execute(
        select(func.count()).select_from(Beat).where(Beat.qc_passed == True)
    )
    qc_passed_count = qc_passed_result.scalar() or 0
    qc_pass_rate = round((qc_passed_count / qc_total) * 100, 1) if qc_total > 0 else 0

    # Total revenue
    total_revenue_result = await db.execute(select(func.sum(Sale.price)))
    total_revenue = float(total_revenue_result.scalar() or 0)

    # Revenue today
    revenue_today_result = await db.execute(
        select(func.sum(Sale.price)).where(Sale.created_at >= today)
    )
    revenue_today = float(revenue_today_result.scalar() or 0)

    # Revenue this week
    revenue_week_result = await db.execute(
        select(func.sum(Sale.price)).where(Sale.created_at >= week_start)
    )
    revenue_this_week = float(revenue_week_result.scalar() or 0)

    # Revenue this month
    revenue_month_result = await db.execute(
        select(func.sum(Sale.price)).where(Sale.created_at >= month_start)
    )
    revenue_this_month = float(revenue_month_result.scalar() or 0)

    # Total sales
    total_sales_result = await db.execute(select(func.count()).select_from(Sale))
    total_sales = total_sales_result.scalar() or 0

    # Average order value
    avg_order_value = round(total_revenue / total_sales, 2) if total_sales > 0 else 0

    # Queue depth (queued + processing)
    queue_depth_result = await db.execute(
        select(func.count()).select_from(RenderJob).where(
            RenderJob.status.in_(["queued", "processing"])
        )
    )
    queue_depth = queue_depth_result.scalar() or 0

    # Success rate from render_jobs
    total_jobs_result = await db.execute(select(func.count()).select_from(RenderJob))
    total_jobs = total_jobs_result.scalar() or 0
    completed_jobs_result = await db.execute(
        select(func.count()).select_from(RenderJob).where(RenderJob.status == "completed")
    )
    completed_jobs = completed_jobs_result.scalar() or 0
    success_rate = round((completed_jobs / total_jobs) * 100, 1) if total_jobs > 0 else 0

    # Average generation time
    avg_gen_time_result = await db.execute(
        select(func.avg(Beat.generation_time_seconds)).where(
            Beat.generation_time_seconds.isnot(None)
        )
    )
    avg_gen_time = round(avg_gen_time_result.scalar() or 0, 1)

    # Average cost per beat
    avg_cost_result = await db.execute(
        select(func.avg(Beat.generation_cost)).where(Beat.generation_cost.isnot(None))
    )
    avg_cost_per_beat = round(float(avg_cost_result.scalar() or 0), 4)

    # Rejection reasons from qc_results
    rejection_reasons = {}
    # qc_results is JSON; we can't easily aggregate in SQL without specific structure,
    # so we fetch failed beats and inspect qc_results manually
    failed_beats_result = await db.execute(
        select(Beat.qc_results).where(Beat.qc_passed == False, Beat.qc_results.isnot(None))
    )
    for row in failed_beats_result.all():
        qc_data = row[0] or {}
        if isinstance(qc_data, dict):
            for reason, detail in qc_data.items():
                rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

    # GPU utilization / avg render time from render_jobs with result_data
    avg_render_time_result = await db.execute(
        select(func.avg(
            func.extract("epoch", RenderJob.completed_at) - func.extract("epoch", RenderJob.started_at)
        )).where(
            RenderJob.completed_at.isnot(None),
            RenderJob.started_at.isnot(None)
        )
    )
    avg_render_time = round(avg_render_time_result.scalar() or 0, 1)

    return {
        "generation": {
            "beats_today": beats_today,
            "beats_this_week": beats_this_week,
            "beats_this_month": beats_this_month,
            "avg_generation_time": avg_gen_time,
            "success_rate": success_rate,
            "avg_cost_per_beat": avg_cost_per_beat
        },
        "quality": {
            "qc_pass_rate": qc_pass_rate,
            "avg_quality_score": avg_quality,
            "rejection_reasons": rejection_reasons
        },
        "sales": {
            "revenue_today": revenue_today,
            "revenue_this_week": revenue_this_week,
            "revenue_this_month": revenue_this_month,
            "total_sales": total_sales,
            "conversion_rate": 0,  # Needs view data; keep 0 until implemented
            "avg_order_value": avg_order_value
        },
        "infrastructure": {
            "workers_online": 0,  # Needs worker heartbeat table; keep 0 until implemented
            "queue_depth": queue_depth,
            "gpu_utilization": 0,  # Needs GPU metrics; keep 0 until implemented
            "avg_render_time": avg_render_time
        }
    }


@router.get("/generation")
async def get_generation_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get generation analytics."""
    # Base beat query with optional date filter
    beat_filter = []
    if start_date:
        beat_filter.append(Beat.created_at >= start_date)
    if end_date:
        beat_filter.append(Beat.created_at <= end_date)

    # Total beats
    total_query = select(func.count()).select_from(Beat)
    if beat_filter:
        total_query = total_query.where(*beat_filter)
    total_result = await db.execute(total_query)
    total_beats = total_result.scalar() or 0

    # Beats grouped by genre
    genre_query = (
        select(Genre.name, func.count(Beat.id))
        .join(Beat, Beat.genre_id == Genre.id)
    )
    if beat_filter:
        genre_query = genre_query.where(*beat_filter)
    genre_query = genre_query.group_by(Genre.name)
    genre_result = await db.execute(genre_query)
    by_genre = {name: count for name, count in genre_result.all()}

    # Beats grouped by status
    status_query = select(Beat.status, func.count(Beat.id))
    if beat_filter:
        status_query = status_query.where(*beat_filter)
    status_query = status_query.group_by(Beat.status)
    status_result = await db.execute(status_query)
    by_status = {status: count for status, count in status_result.all()}

    # Average quality by genre
    avg_quality_query = (
        select(Genre.name, func.avg(Beat.quality_score))
        .join(Beat, Beat.genre_id == Genre.id)
        .where(Beat.quality_score.isnot(None))
    )
    if beat_filter:
        avg_quality_query = avg_quality_query.where(*beat_filter)
    avg_quality_query = avg_quality_query.group_by(Genre.name)
    avg_quality_result = await db.execute(avg_quality_query)
    avg_quality_by_genre = {
        name: round(float(avg_q), 2) for name, avg_q in avg_quality_result.all()
    }

    # Generation time trend (daily average for last 30 days)
    trend_start = datetime.utcnow() - timedelta(days=30)
    trend_query = (
        select(
            func.date(Beat.created_at),
            func.avg(Beat.generation_time_seconds)
        )
        .where(
            Beat.generation_time_seconds.isnot(None),
            Beat.created_at >= trend_start
        )
        .group_by(func.date(Beat.created_at))
        .order_by(func.date(Beat.created_at))
    )
    trend_result = await db.execute(trend_query)
    generation_time_trend = [
        {"date": str(date), "avg_time": round(float(avg_t), 1)}
        for date, avg_t in trend_result.all()
    ]

    return {
        "total_beats": total_beats,
        "by_genre": by_genre,
        "by_status": by_status,
        "avg_quality_by_genre": avg_quality_by_genre,
        "generation_time_trend": generation_time_trend
    }


@router.get("/sales")
async def get_sales_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get sales analytics."""
    sale_filter = []
    if start_date:
        sale_filter.append(Sale.created_at >= start_date)
    if end_date:
        sale_filter.append(Sale.created_at <= end_date)

    # Total revenue
    revenue_query = select(func.sum(Sale.price))
    if sale_filter:
        revenue_query = revenue_query.where(*sale_filter)
    revenue_result = await db.execute(revenue_query)
    total_revenue = float(revenue_result.scalar() or 0)

    # Total sales count
    sales_count_query = select(func.count()).select_from(Sale)
    if sale_filter:
        sales_count_query = sales_count_query.where(*sale_filter)
    sales_count_result = await db.execute(sales_count_query)
    total_sales = sales_count_result.scalar() or 0

    # Sales by license type
    license_query = select(Sale.license_type, func.count(Sale.id), func.sum(Sale.price))
    if sale_filter:
        license_query = license_query.where(*sale_filter)
    license_query = license_query.group_by(Sale.license_type)
    license_result = await db.execute(license_query)
    by_license_type = {
        lic_type: {"count": count, "revenue": float(rev)}
        for lic_type, count, rev in license_result.all()
    }

    # Sales by genre
    genre_sales_query = (
        select(Genre.name, func.count(Sale.id), func.sum(Sale.price))
        .join(Beat, Sale.beat_id == Beat.id)
        .join(Genre, Beat.genre_id == Genre.id)
    )
    if sale_filter:
        genre_sales_query = genre_sales_query.where(*sale_filter)
    genre_sales_query = genre_sales_query.group_by(Genre.name)
    genre_sales_result = await db.execute(genre_sales_query)
    by_genre = {
        name: {"count": count, "revenue": float(rev)}
        for name, count, rev in genre_sales_result.all()
    }

    # Top selling beats
    top_beats_query = (
        select(Beat.id, Beat.title, func.count(Sale.id), func.sum(Sale.price))
        .join(Sale, Sale.beat_id == Beat.id)
    )
    if sale_filter:
        top_beats_query = top_beats_query.where(*sale_filter)
    top_beats_query = (
        top_beats_query.group_by(Beat.id, Beat.title)
        .order_by(desc(func.count(Sale.id)))
        .limit(10)
    )
    top_beats_result = await db.execute(top_beats_query)
    top_beats = [
        {
            "beat_id": str(beat_id),
            "title": title,
            "sales_count": count,
            "revenue": float(rev)
        }
        for beat_id, title, count, rev in top_beats_result.all()
    ]

    # Revenue trend (daily for last 30 days)
    trend_start = datetime.utcnow() - timedelta(days=30)
    trend_query = (
        select(
            func.date(Sale.created_at),
            func.sum(Sale.price),
            func.count(Sale.id)
        )
        .where(Sale.created_at >= trend_start)
        .group_by(func.date(Sale.created_at))
        .order_by(func.date(Sale.created_at))
    )
    trend_result = await db.execute(trend_query)
    revenue_trend = [
        {"date": str(date), "revenue": float(rev), "sales": count}
        for date, rev, count in trend_result.all()
    ]

    return {
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "by_license_type": by_license_type,
        "by_genre": by_genre,
        "top_beats": top_beats,
        "revenue_trend": revenue_trend
    }


@router.get("/quality")
async def get_quality_analytics(db: AsyncSession = Depends(get_db)):
    """Get quality control analytics."""
    # Pass rate
    qc_total_result = await db.execute(
        select(func.count()).select_from(Beat).where(Beat.qc_passed.isnot(None))
    )
    qc_total = qc_total_result.scalar() or 0
    qc_passed_result = await db.execute(
        select(func.count()).select_from(Beat).where(Beat.qc_passed == True)
    )
    qc_passed_count = qc_passed_result.scalar() or 0
    pass_rate = round((qc_passed_count / qc_total) * 100, 1) if qc_total > 0 else 0

    # Average scores by check type from QCLog
    avg_scores_query = (
        select(QCLog.check_type, func.avg(QCLog.score))
        .where(QCLog.score.isnot(None))
        .group_by(QCLog.check_type)
    )
    avg_scores_result = await db.execute(avg_scores_query)
    avg_scores = {
        check_type: round(float(avg_s), 2)
        for check_type, avg_s in avg_scores_result.all()
    }

    # Failure reasons
    failure_reasons = {}
    failed_beats_result = await db.execute(
        select(Beat.qc_results).where(Beat.qc_passed == False, Beat.qc_results.isnot(None))
    )
    for row in failed_beats_result.all():
        qc_data = row[0] or {}
        if isinstance(qc_data, dict):
            for reason, detail in qc_data.items():
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

    # Quality trend (daily avg quality score for last 30 days)
    trend_start = datetime.utcnow() - timedelta(days=30)
    trend_query = (
        select(
            func.date(Beat.created_at),
            func.avg(Beat.quality_score)
        )
        .where(
            Beat.quality_score.isnot(None),
            Beat.created_at >= trend_start
        )
        .group_by(func.date(Beat.created_at))
        .order_by(func.date(Beat.created_at))
    )
    trend_result = await db.execute(trend_query)
    quality_trend = [
        {"date": str(date), "avg_score": round(float(avg_s), 2)}
        for date, avg_s in trend_result.all()
    ]

    return {
        "pass_rate": pass_rate,
        "avg_scores": avg_scores,
        "failure_reasons": failure_reasons,
        "quality_trend": quality_trend
    }


@router.get("/ai-learning")
async def get_ai_learning_metrics(db: AsyncSession = Depends(get_db)):
    """Get AI learning and model performance metrics."""
    from shared.db.models import AIModel, LearningFeedback

    # Active models
    active_models_result = await db.execute(
        select(AIModel).where(AIModel.is_active == True)
    )
    active_models = [
        {"id": str(m.id), "name": m.name, "version": m.version, "type": m.model_type}
        for m in active_models_result.scalars().all()
    ]

    # Model performance from metrics JSON
    model_perf_result = await db.execute(select(AIModel))
    model_performance = {}
    for model in model_perf_result.scalars().all():
        model_performance[str(model.id)] = {
            "name": model.name,
            "version": model.version,
            "metrics": model.metrics or {}
        }

    # Feedback stats
    feedback_stats_result = await db.execute(
        select(LearningFeedback.feedback_type, func.count(LearningFeedback.id))
        .group_by(LearningFeedback.feedback_type)
    )
    feedback_stats = {
        ftype: count for ftype, count in feedback_stats_result.all()
    }

    # Improvement trend (feedback count over last 30 days)
    trend_start = datetime.utcnow() - timedelta(days=30)
    trend_query = (
        select(
            func.date(LearningFeedback.created_at),
            func.count(LearningFeedback.id)
        )
        .where(LearningFeedback.created_at >= trend_start)
        .group_by(func.date(LearningFeedback.created_at))
        .order_by(func.date(LearningFeedback.created_at))
    )
    trend_result = await db.execute(trend_query)
    improvement_trend = [
        {"date": str(date), "feedback_count": count}
        for date, count in trend_result.all()
    ]

    return {
        "active_models": active_models,
        "model_performance": model_performance,
        "feedback_stats": feedback_stats,
        "improvement_trend": improvement_trend
    }
