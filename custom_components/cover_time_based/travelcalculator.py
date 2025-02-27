"""
Source: https://github.com/XKNX/xknx/blob/afc21f762ecc485b05d8e3125d0448f04436d0b2/xknx/devices/travelcalculator.py
MIT License

Module TravelCalculator provides functionality for predicting the current position of a Cover.

E.g.:

* Given a Cover that takes 100 seconds to travel from top to bottom.
* Starting from position 90, directed to position 60 at time 0.
* At time 10 TravelCalculator will return position 80 (final position not reached).
* At time 20 TravelCalculator will return position 70 (final position not reached).
* At time 30 TravelCalculator will return position 60 (final position reached).
"""

from __future__ import annotations

import time
from enum import Enum


class TravelStatus(Enum):
    """Enum class for travel status."""

    DIRECTION_UP = 1
    DIRECTION_DOWN = 2
    STOPPED = 3


class TravelCalculator:
    """Class for calculating the current position of a cover."""

    __slots__ = (
        "travel_direction",
        "travel_time_down",
        "travel_time_up",
        "slats_open_time",
        "slats_close_time",
        "_last_known_position",
        "_last_known_position_timestamp",
        "_position_confirmed",
        "_travel_to_position",
        "position_closed",
        "position_open",
    )

    def __init__(self, travel_time_down: float, travel_time_up: float, slats_open_time: float, slats_close_time: float) -> None:
        """Initialize TravelCalculator class."""
        self.travel_direction = TravelStatus.STOPPED
        self.travel_time_down = travel_time_down
        self.travel_time_up = travel_time_up
        self.slats_open_time = slats_open_time
        self.slats_close_time = slats_close_time

        self._last_known_position: int | None = None
        self._last_known_position_timestamp: float = 0.0
        self._position_confirmed: bool = False
        self._travel_to_position: int | None = None

        # 100 is closed, 0 is fully open
        self.position_closed: int = 100
        self.position_open: int = 0

    def set_position(self, position: int) -> None:
        """Set the current position."""
        self._last_known_position = position
        self._last_known_position_timestamp = time.time()
        self._position_confirmed = True

    def update_position(self, position: int) -> None:
        """Update known position of cover."""
        self._last_known_position = position
        self._last_known_position_timestamp = time.time()
        if position == self._travel_to_position:
            self._position_confirmed = True

    def stop(self) -> None:
        """Stop traveling."""
        stop_position = self.current_position()
        if stop_position is None:
            return
        self._last_known_position = stop_position
        self._travel_to_position = stop_position
        self._position_confirmed = False
        self.travel_direction = TravelStatus.STOPPED

    def start_travel(self, _travel_to_position: int) -> None:
        """Start traveling to position."""
        if self._last_known_position is None:
            self.set_position(_travel_to_position)
            return
        self.stop()
        self._last_known_position_timestamp = time.time()
        self._travel_to_position = _travel_to_position
        self._position_confirmed = False

        self.travel_direction = (
            TravelStatus.DIRECTION_DOWN
            if _travel_to_position > self._last_known_position
            else TravelStatus.DIRECTION_UP
        )

    def start_travel_up(self) -> None:
        """Start traveling up."""
        self.start_travel(self.position_open)

    def start_travel_down(self) -> None:
        """Start traveling down."""
        self.start_travel(self.position_closed)

    def start_travel_tilt(self, _travel_to_position: int) -> None:
        """Start traveling tilt to position."""
        if self._last_known_position is None:
            self.set_position(_travel_to_position)
            return
        self.stop()
        self._last_known_position_timestamp = time.time()
        self._travel_to_position = _travel_to_position
        self._position_confirmed = False

        self.travel_direction = (
            TravelStatus.DIRECTION_DOWN
            if _travel_to_position > self._last_known_position
            else TravelStatus.DIRECTION_UP
        )

    def start_travel_tilt_up(self) -> None:
        """Start traveling tilt up."""
        self.start_travel_tilt(self.position_open)

    def start_travel_tilt_down(self) -> None:
        """Start traveling tilt down."""
        self.start_travel_tilt(self.position_closed)

    def current_position(self) -> int | None:
        """Return current (calculated or known) position."""
        if not self._position_confirmed:
            return self._calculate_position()
        return self._last_known_position

    def is_traveling(self) -> bool:
        """Return if cover is traveling."""
        return self.current_position() != self._travel_to_position

    def is_opening(self) -> bool:
        """Return if the cover is opening."""
        return (
            self.is_traveling() and self.travel_direction == TravelStatus.DIRECTION_UP
        )

    def is_closing(self) -> bool:
        """Return if the cover is closing."""
        return (
            self.is_traveling() and self.travel_direction == TravelStatus.DIRECTION_DOWN
        )

    def position_reached(self) -> bool:
        """Return if cover has reached designated position."""
        return self.current_position() == self._travel_to_position

    def is_open(self) -> bool:
        """Return if cover is (fully) open."""
        return self.current_position() == self.position_open

    def is_closed(self) -> bool:
        """Return if cover is (fully) closed."""
        return self.current_position() == self.position_closed

    def _calculate_position(self) -> int | None:
        """Return calculated position."""
        if self._travel_to_position is None or self._last_known_position is None:
            return self._last_known_position
        relative_position = self._travel_to_position - self._last_known_position

        def position_reached_or_exceeded(relative_position: int) -> bool:
            """Return if designated position was reached."""
            if (
                relative_position <= 0
                and self.travel_direction == TravelStatus.DIRECTION_DOWN
            ):
                return True
            if (
                relative_position >= 0
                and self.travel_direction == TravelStatus.DIRECTION_UP
            ):
                return True
            return False

        if position_reached_or_exceeded(relative_position):
            return self._travel_to_position

        remaining_travel_time = self.calculate_travel_time(
            from_position=self._last_known_position,
            to_position=self._travel_to_position,
        )
        elapsed_time = time.time() - self._last_known_position_timestamp

        if elapsed_time > remaining_travel_time:
            return self._travel_to_position

        # Calculate the progress considering slats time
        slats_time = 0
        if self._last_known_position == 0 or self._travel_to_position == 0:
            slats_time = self.slats_close_time if self.travel_direction == TravelStatus.DIRECTION_DOWN else self.slats_open_time
        if elapsed_time < slats_time:
            # During slats adjustment, position changes very slowly
            progress = elapsed_time / slats_time * 0.1  # Assume 10% of the movement during slats adjustment
        else:
            # Normal movement after slats adjustment
            progress = (elapsed_time - slats_time) / (remaining_travel_time - slats_time)

        return int(self._last_known_position + relative_position * progress)

    def calculate_travel_time(self, from_position: int, to_position: int) -> float:
        """Calculate time to travel from one position to another."""
        travel_range = abs(to_position - from_position)
        travel_time_full = (
            self.travel_time_down if from_position > to_position else self.travel_time_up
        )
        slats_time = 0
        if from_position == 0 or to_position == 0:
            slats_time = self.slats_close_time if from_position > to_position else self.slats_open_time
        return (travel_time_full - slats_time) * (travel_range / 100) + slats_time
