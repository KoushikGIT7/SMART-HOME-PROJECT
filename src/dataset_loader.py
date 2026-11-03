"""
Module 1: Dataset Loader
========================
Downloads the UCI Household Power Consumption dataset on first run,
caches it locally, and returns the raw text file path.
"""

from __future__ import annotations

import os
import zipfile
import logging
from pathlib import Path

import requests
import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML configuration from file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Dataset Loader
# ---------------------------------------------------------------------------

class DatasetLoader:
    """
    Downloads and caches the UCI Household Power Consumption dataset.

    On the first call to ``get_raw_path()``, the dataset is downloaded
    from the UCI repository, extracted, and saved to ``data/raw/``.
    Subsequent calls immediately return the cached file path.
    """

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        ds = cfg["dataset"]
        self.url: str = ds["url"]
        self.raw_dir: Path = Path(ds["raw_dir"])
        self.cache_file: Path = Path(ds["cache_file"])
        self.zip_file: Path = Path(ds["zip_file"])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_raw_path(self) -> Path:
        """Return the path to the raw data file, downloading if needed."""
        if self.cache_file.exists():
            logger.info("Dataset already cached at %s", self.cache_file)
            return self.cache_file

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self._download()
        self._extract()
        return self.cache_file

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _download(self) -> None:
        """Stream-download the ZIP archive with a progress indicator."""
        logger.info("Downloading dataset from %s …", self.url)
        response = requests.get(self.url, stream=True, timeout=120)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(self.zip_file, "wb") as fh:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    fh.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        logger.debug("Download progress: %.1f%%", pct)

        logger.info("Download complete → %s", self.zip_file)

    def _extract(self) -> None:
        """Extract the ZIP archive into the raw data directory."""
        logger.info("Extracting %s …", self.zip_file)
        with zipfile.ZipFile(self.zip_file, "r") as z:
            z.extractall(self.raw_dir)
        logger.info("Extraction complete → %s", self.raw_dir)

        # Clean up ZIP to save space
        try:
            os.remove(self.zip_file)
        except OSError:
            pass
