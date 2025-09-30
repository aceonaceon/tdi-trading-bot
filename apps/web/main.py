from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from wsgiref.simple_server import make_server

from apps.bot.migrations import run_migrations
from apps.common.config import WebConfig
from apps.common.database import create_database

config = WebConfig()
db = create_database(config.db_url)
run_migrations(config.db_url)


@dataclass(slots=True)
class DashboardSummary:
    trades_count: int = 0
    latest_equity: float = 0.0
    latest_drawdown: float = 0.0
    last_ts: datetime | None = None


def _fetch_summary() -> DashboardSummary:
    summary = DashboardSummary()
    with db.connect() as conn:
        cursor = conn.execute("SELECT COUNT(*) AS c FROM trades")
        row = cursor.fetchone()
        if row:
            summary.trades_count = int(row["c"])
        cursor = conn.execute("SELECT ts, equity, dd FROM equity_curve ORDER BY ts DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            summary.latest_equity = float(row["equity"])
            summary.latest_drawdown = float(row["dd"])
            summary.last_ts = datetime.fromisoformat(row["ts"])
    return summary


def _render_dashboard(summary: DashboardSummary) -> str:
    ts_text = summary.last_ts.strftime("%Y-%m-%d %H:%M:%S") if summary.last_ts else "—"
    return f"""
    <html>
        <head>
            <title>TDI Trading Dashboard</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 2rem;
                    background-color: #0f172a;
                    color: #f8fafc;
                }}
                .card {{
                    background-color: #1e293b;
                    padding: 1.5rem;
                    border-radius: 12px;
                    margin-bottom: 1rem;
                }}
                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 1rem;
                }}
                h1 {{
                    margin-bottom: 1rem;
                }}
                span.label {{
                    display: block;
                    font-size: 0.85rem;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    color: #94a3b8;
                }}
                span.value {{
                    font-size: 1.8rem;
                    font-weight: bold;
                    color: #38bdf8;
                }}
            </style>
        </head>
        <body>
            <h1>Paper Trading Dashboard</h1>
            <div class="metrics">
                <div class="card">
                    <span class="label">Run ID</span>
                    <span class="value">{config.run_id or "—"}</span>
                </div>
                <div class="card">
                    <span class="label">Trades</span>
                    <span class="value">{summary.trades_count}</span>
                </div>
                <div class="card">
                    <span class="label">Latest Equity</span>
                    <span class="value">{summary.latest_equity:,.2f}</span>
                </div>
                <div class="card">
                    <span class="label">Drawdown</span>
                    <span class="value">{summary.latest_drawdown:,.4f}</span>
                </div>
                <div class="card">
                    <span class="label">Last Tick</span>
                    <span class="value">{ts_text}</span>
                </div>
            </div>
        </body>
    </html>
    """


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path == "/healthz":
        payload = json.dumps({"status": "ok", "mode": config.mode}).encode()
        start_response(
            "200 OK", [("Content-Type", "application/json"), ("Content-Length", str(len(payload)))]
        )
        return [payload]

    if path == "/":
        summary = _fetch_summary()
        body = _render_dashboard(summary).encode()
        start_response(
            "200 OK",
            [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))],
        )
        return [body]

    start_response("404 Not Found", [("Content-Type", "text/plain"), ("Content-Length", "0")])
    return [b""]


def serve(port: int) -> None:
    with make_server("0.0.0.0", port, application) as httpd:  # noqa: S104 - required for local development
        httpd.serve_forever()


if __name__ == "__main__":
    serve(config.dashboard_port)
