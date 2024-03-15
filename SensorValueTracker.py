from collections import deque
from datetime import datetime, timedelta
from typing import Deque, Optional, Tuple

class SensorValueTracker:
    def __init__(self, threshold_seconds: int, percentage: float = 95.0):
        self.threshold_seconds: int = threshold_seconds
        self.percentage: float = percentage
        self.readings: Deque[Tuple[datetime, int]] = deque()  # Store (timestamp, value) tuples

    def report_value(self, value: int, timestamp: Optional[datetime] = None) -> None:
        if timestamp is None:
            timestamp = datetime.now()
        self.readings.append((timestamp, value))
        self.clean_old_readings()

    def clean_old_readings(self) -> None:
        """Remove readings older than threshold_seconds."""
        now = datetime.now()
        while self.readings and now - self.readings[0][0] > timedelta(seconds=self.threshold_seconds):
            self.readings.popleft()

    def get_most_common_value(self) -> Tuple[Optional[int], int]:
        """Get the most common value and its count from the current readings."""
        if not self.readings:
            return None, 0
        value_counts: dict = {}
        for _, value in self.readings:
            value_counts[value] = value_counts.get(value, 0) + 1
        most_common_value = max(value_counts, key=value_counts.get, default=None)
        return most_common_value, value_counts.get(most_common_value, 0)

    def get_value(self) -> Optional[int]:
        most_common_value, count = self.get_most_common_value()
        if count >= (len(self.readings) * self.percentage / 100):
            return most_common_value
        return None