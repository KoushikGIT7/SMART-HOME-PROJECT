"""
Module 9: Replay Simulator
===========================
Simulates real-time hourly streaming of historical data using
Streamlit's session state.  Supports play/pause, variable speed,
and a timeline slider.
"""

from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

# Session state keys
_KEY_PLAYING = "replay_playing"
_KEY_IDX = "replay_idx"
_KEY_SPEED = "replay_speed"
_KEY_MAX = "replay_max"
_KEY_INIT = "replay_initialized"


class ReplaySimulator:
    """
    Manages replay state in ``st.session_state``.

    Usage (in a Streamlit page)
    ---------------------------
    ```python
    sim = ReplaySimulator(df)
    sim.render_controls()          # draw play/pause/speed widgets
    window = sim.current_window(hours=24)  # get current 24-hour slice
    ```
    """

    def __init__(self, df: pd.DataFrame, window_hours: int = 48):
        self.df = df
        self.window_hours = window_hours
        self._init_state()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render_controls(self) -> None:
        """Render play/pause, speed selector, and timeline slider."""
        col1, col2, col3 = st.columns([1, 1, 4])

        with col1:
            is_playing = st.session_state.get(_KEY_PLAYING, False)
            label = "⏸️ Pause" if is_playing else "▶️ Play"
            if st.button(label, key="replay_playpause_btn", use_container_width=True):
                st.session_state[_KEY_PLAYING] = not is_playing
                st.rerun()

        with col2:
            from src.dataset_loader import load_config
            cfg = load_config()
            speeds = cfg["ui"]["replay_speeds"]
            st.session_state[_KEY_SPEED] = st.selectbox(
                "Speed",
                options=speeds,
                index=0,
                format_func=lambda x: f"{x}×",
                key="replay_speed_select",
            )

        with col3:
            max_idx = st.session_state.get(_KEY_MAX, len(self.df) - 1)
            idx = st.session_state.get(_KEY_IDX, 0)
            new_idx = st.slider(
                "Timeline",
                min_value=0,
                max_value=max(0, max_idx - self.window_hours),
                value=idx,
                step=1,
                key="replay_timeline_slider",
                format="%d",
            )
            if new_idx != idx:
                st.session_state[_KEY_IDX] = new_idx

    def current_window(self) -> pd.DataFrame:
        """Return the current window of data based on replay position."""
        idx = st.session_state.get(_KEY_IDX, 0)
        end = min(idx + self.window_hours, len(self.df))
        return self.df.iloc[idx:end]

    def advance(self) -> bool:
        """
        Advance the replay position by ``speed`` steps.

        Returns True if the replay is still active (not at end).
        Should be called after rendering the current frame.
        """
        if not st.session_state.get(_KEY_PLAYING, False):
            return False

        speed = st.session_state.get(_KEY_SPEED, 1)
        idx = st.session_state.get(_KEY_IDX, 0)
        max_idx = st.session_state.get(_KEY_MAX, len(self.df) - 1)

        new_idx = idx + speed
        if new_idx >= max_idx - self.window_hours:
            st.session_state[_KEY_PLAYING] = False
            return False

        st.session_state[_KEY_IDX] = new_idx
        return True

    def get_timestamp(self) -> pd.Timestamp:
        """Return the current timestamp at the replay head."""
        idx = st.session_state.get(_KEY_IDX, 0)
        return self.df.index[min(idx, len(self.df) - 1)]

    def reset(self) -> None:
        """Reset replay to the beginning."""
        st.session_state[_KEY_IDX] = 0
        st.session_state[_KEY_PLAYING] = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_state(self) -> None:
        if not st.session_state.get(_KEY_INIT, False):
            st.session_state[_KEY_PLAYING] = False
            st.session_state[_KEY_IDX] = 0
            st.session_state[_KEY_SPEED] = 1
            st.session_state[_KEY_MAX] = len(self.df) - 1
            st.session_state[_KEY_INIT] = True
