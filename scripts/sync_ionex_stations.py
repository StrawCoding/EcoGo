#!/usr/bin/env python3
"""Pre-fetch Ionex swap stations from the same API used by map.ionex.com.tw.

Writes a slim EcoGo cache JSON (no API key). Intended for cron / manual sync.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://api.ionex.com.tw/location"
UA = "EcoGoStationSync/1.0 (+https://ecogo.wastebase.xyz/; cache sync)"


def fetch_locations() -> dict:
    req = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": UA,
            "Accept": "application/json",
            "Origin": "https://map.ionex.com.tw",
            "Referer": "https://map.ionex.com.tw/",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        payload = json.load(resp)
    if not isinstance(payload, dict) or payload.get("status") != 200:
        raise RuntimeError(f"unexpected Ionex API response: status={payload.get('status') if isinstance(payload, dict) else type(payload)}")
    return payload


def to_ecogo_stations(payload: dict) -> list[dict]:
    stations: list[dict] = []
    for item in payload.get("data") or []:
        if item.get("type") != "station":
            continue
        try:
            lat = float(item.get("lat"))
            lon = float(item.get("lng"))
        except (TypeError, ValueError):
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        if abs(lat) < 1e-6 and abs(lon) < 1e-6:
            continue
        sid = item.get("id")
        stations.append(
            {
                "id": f"ionex-{sid}",
                "name": str(item.get("name") or f"Ionex {sid}"),
                "type": "ionex",
                "lat": round(lat, 7),
                "lon": round(lon, 7),
                "city": item.get("city") or "",
                "district": item.get("district") or "",
                "address": item.get("address") or "",
                "operating_status": item.get("operating_status") or "",
                "unique_key": item.get("unique_key") or "",
            }
        )

    seen: set[str] = set()
    uniq: list[dict] = []
    for s in stations:
        key = s["unique_key"] or f"{s['lat']:.5f},{s['lon']:.5f}"
        if key in seen:
            continue
        seen.add(key)
        uniq.append(s)
    return uniq


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Sync Ionex stations cache for EcoGo")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=root / "data" / "stations-ionex.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--deploy",
        type=Path,
        default=None,
        help="Also copy to deploy path (default: 1panel site index dir if present)",
    )
    args = parser.parse_args()

    deploy = args.deploy
    if deploy is None:
        candidate = Path("/opt/1panel/www/sites/ecogo.wastebase.xyz/index/stations-ionex.json")
        if candidate.parent.is_dir():
            deploy = candidate

    payload = fetch_locations()
    stations = to_ecogo_stations(payload)
    if len(stations) < 100:
        raise RuntimeError(f"too few stations: {len(stations)}")

    out = {
        "source": API_URL,
        "via": "https://map.ionex.com.tw/",
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(stations),
        "stations": stations,
    }
    text = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    if deploy is not None:
        deploy.parent.mkdir(parents=True, exist_ok=True)
        deploy.write_text(text, encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "count": len(stations),
                "output": str(args.output),
                "deploy": str(deploy) if deploy else None,
                "bytes": len(text.encode("utf-8")),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — CLI exit message
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
