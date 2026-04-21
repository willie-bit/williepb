"""Command-line entrypoint (`williepb ...`).

Intentionally minimal. Heavy lifting lives in services/jobs — the CLI only
parses args and prints results.
"""

from __future__ import annotations

import json
from datetime import date as date_cls
from datetime import datetime

import typer

from app.db.session import SessionLocal, init_db
from app.jobs.daily_sync import run_daily_sync
from app.services.dashboard import build_dashboard

app = typer.Typer(help="williepb family asset management CLI")


@app.command("init-db")
def cmd_init_db() -> None:
    """Create database tables (idempotent)."""
    init_db()
    typer.echo("✓ schema ready")


@app.command("sync")
def cmd_sync(on_date: str | None = typer.Option(None, help="YYYY-MM-DD; default: today")) -> None:
    """Run the daily price sync + snapshot for every household."""
    target = _parse_date(on_date)
    reports = run_daily_sync(target)
    for hh_id, rep in reports.items():
        typer.echo(
            f"household={hh_id} prices_written={rep.prices_written} errors={len(rep.errors)}"
        )
        for err in rep.errors:
            typer.echo(f"  ! {err}")


@app.command("dashboard")
def cmd_dashboard(
    household_id: int,
    on_date: str | None = typer.Option(None, help="YYYY-MM-DD; default: today"),
) -> None:
    """Print a household dashboard JSON."""
    target = _parse_date(on_date)
    with SessionLocal() as db:
        payload = build_dashboard(db, household_id, target).model_dump(mode="json")
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def _parse_date(raw: str | None) -> date_cls:
    if raw is None:
        return date_cls.today()
    return datetime.strptime(raw, "%Y-%m-%d").date()


if __name__ == "__main__":
    app()
