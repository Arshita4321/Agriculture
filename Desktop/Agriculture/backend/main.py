
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
CROP_FILE = ROOT / "data" / "raw" / "crop_yield.csv"
WEATHER_FILE = ROOT / "data" / "raw" / "ludhiana_weather.csv"

app = FastAPI(title="AgriRisk Intelligence API")

# Local React development server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_crop_data():
    if not CROP_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Crop dataset not found in data/raw/",
        )
    return pd.read_csv(CROP_FILE)


def load_weather_data():
    if not WEATHER_FILE.exists():
        return None

    lines = WEATHER_FILE.read_text(
        encoding="utf-8-sig"
    ).splitlines()

    header = next(
        (
            i for i, line in enumerate(lines)
            if line.strip().startswith("YEAR,MO,DY,")
        ),
        None,
    )

    if header is None:
        return None

    df = pd.read_csv(WEATHER_FILE, skiprows=header)
    df.columns = [c.strip().upper() for c in df.columns]

    required = [
        "YEAR", "MO", "DY", "PRECTOTCORR",
        "T2M", "T2M_MAX", "T2M_MIN",
    ]

    if not set(required).issubset(df.columns):
        return None

    df = df[required].copy()
    df["date"] = pd.to_datetime(
        dict(year=df.YEAR, month=df.MO, day=df.DY),
        errors="coerce",
    )

    for col in required[3:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[df[col] <= -999, col] = float("nan")

    df = df.dropna(subset=["date"]).sort_values("date")
    return df


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "application": "AgriRisk Intelligence",
    }


@app.get("/api/districts")
def districts():
    # The Kaggle dataset has STATE, not DISTRICT.
    # Do not label states as districts.
    df = load_crop_data()
    states = sorted(df["state"].dropna().astype(str).unique())
    return {"states": states, "districts": []}


@app.get("/api/analytics")
def analytics():
    df = load_crop_data()

    df["yield"] = pd.to_numeric(df["yield"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["yield", "year"])

    yearly = (
        df.groupby("year", as_index=False)["yield"]
        .mean()
        .sort_values("year")
    )

    crop_yield = (
        df.groupby("crop", as_index=False)["yield"]
        .mean()
        .sort_values("yield", ascending=False)
        .head(10)
    )

    return {
        "source": "Kaggle crop_yield.csv",
        "total_records": int(len(df)),
        "crop_count": int(df["crop"].nunique()),
        "state_count": int(df["state"].nunique()),
        "average_yield": float(df["yield"].mean()),
        "yearly_yield": [
            {"year": int(r.year), "yield": float(r["yield"])}
            for _, r in yearly.iterrows()
        ],
        "crop_comparison": [
            {"crop": str(r.crop), "yield": float(r["yield"])}
            for _, r in crop_yield.iterrows()
        ],
    }


@app.get("/api/risk")
def risk(
    crop: str = Query(default="Wheat"),
):
    weather = load_weather_data()

    if weather is None or weather.empty:
        raise HTTPException(
            status_code=503,
            detail=(
                "Weather data is unavailable or its CSV header "
                "could not be parsed."
            ),
        )

    latest = weather.dropna(
        subset=["PRECTOTCORR", "T2M"]
    ).tail(7)

    if latest.empty:
        raise HTTPException(
            status_code=503,
            detail="No valid recent weather observations found.",
        )

    # Descriptive indicators only; these are not validated
    # crop-specific risk thresholds.
    return {
        "location": "Ludhiana weather point",
        "crop": crop,
        "latest_date": str(latest["date"].max().date()),
        "rainfall_last_7_observations_mm": float(
            latest["PRECTOTCORR"].sum()
        ),
        "average_temperature_c": float(latest["T2M"].mean()),
        "observations": int(len(latest)),
        "risk_assessment": "Not calibrated",
        "note": (
            "Weather summaries only. A validated agricultural "
            "risk assessment requires historical baselines and "
            "crop-specific thresholds."
        ),
    }
