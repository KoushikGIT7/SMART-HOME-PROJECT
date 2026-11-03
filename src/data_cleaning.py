"""
Module 2: Data Cleaning
=======================
Parses the raw UCI dataset, handles missing values, resamples to
hourly frequency, and returns a clean Pandas DataFrame ready for
feature engineering.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class DataCleaner:
    """
    Cleans and resamples the UCI Household Power Consumption data.

    Steps
    -----
    1. Read CSV (semicolon-delimited, mixed date/time columns)
    2. Replace '?' with NaN
    3. Cast all measurement columns to float
    4. Build a proper DatetimeIndex
    5. Forward-fill gaps (up to 24 consecutive NaN rows)
    6. Resample to hourly mean
    7. Drop any remaining NaN rows
    """

    COLUMNS = [
        "Date",
        "Time",
        "Global_active_power",
        "Global_reactive_power",
        "Voltage",
        "Global_intensity",
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3",
    ]

    NUMERIC_COLUMNS = [
        "Global_active_power",
        "Global_reactive_power",
        "Voltage",
        "Global_intensity",
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3",
    ]

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        self.resample_freq: str = cfg["dataset"]["resample_freq"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def clean(self, raw_path: Path | str) -> pd.DataFrame:
        """
        Load, clean, and resample the raw dataset.

        Parameters
        ----------
        raw_path : path to ``household_power_consumption.txt``

        Returns
        -------
        pd.DataFrame
            Hourly-resampled DataFrame indexed by ``datetime``.
        """
        logger.info("Loading raw data from %s …", raw_path)
        df = self._load(raw_path)
        logger.info("Raw shape: %s", df.shape)

        df = self._parse_datetime(df)
        df = self._cast_numeric(df)
        df = self._fill_gaps(df)
        df = self._resample(df)
        df = self._drop_na(df)

        logger.info("Clean shape after resampling: %s", df.shape)
        return df

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self, path: Path | str) -> pd.DataFrame:
        dtype = {col: "float32" for col in self.NUMERIC_COLUMNS}
        return pd.read_csv(
            path,
            sep=";",
            header=0,
            names=self.COLUMNS,
            na_values=["?", "NA", ""],
            dtype=dtype,
            low_memory=False,
        )

    def _parse_datetime(self, df: pd
    .DataFrame) -> pd.DataFrame:
        dt = pd.to_datetime(
            df["Date"] + " " + df["Time"],
            format="%d/%m/%Y %H:%M:%S",
            errors="coerce",
        )
        df = df.drop(columns=["Date", "Time"])
        df.index = dt
        df.index.name = "datetime"
        return df

    def _cast_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.NUMERIC_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def _fill_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Forward-fill up to 24 consecutive NaN rows (≈ 24 minutes at 1-min freq)."""
        df = df.ffill(limit=24)
        return df

    def _resample(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate to hourly means; sum sub-meters for better physical meaning."""
        agg = {col: "mean" for col in self.NUMERIC_COLUMNS}
        # Sub-meters represent Wh consumed — sum makes more sense over an hour
        for sm in ["Sub_metering_1", "Sub_metering_2", "Sub_metering_3"]:
            if sm in agg:
                agg[sm] = "sum"
        return df.resample(self.resample_freq).agg(agg)

    def _drop_na(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.dropna()
        after = len(df)
        if before - after:
            logger.warning("Dropped %d rows with remaining NaN", before - after)
        return df
