import unittest
from datetime import datetime, timedelta, timezone

from journey import (
    CITIES,
    FIRST_MEMORY,
    MILESTONES,
    NEXT_MEETING,
    TIMEZONE,
    CountdownParts,
    countdown_parts,
    formatted_coordinates,
    route_position,
    timeline_progress,
)


class CountdownTests(unittest.TestCase):
    def test_remaining_parts(self):
        now = NEXT_MEETING - timedelta(days=2, hours=3, minutes=4, seconds=5)
        self.assertEqual(countdown_parts(now), CountdownParts(2, 3, 4, 5))

    def test_target_and_past_are_zero(self):
        for now in (NEXT_MEETING, NEXT_MEETING + timedelta(days=100)):
            with self.subTest(now=now):
                self.assertEqual(countdown_parts(now), (0, 0, 0, 0))

    def test_naive_datetime_means_budapest(self):
        naive = datetime(2026, 11, 11, 23, 30)
        self.assertEqual(countdown_parts(naive), (0, 0, 30, 0))
        self.assertEqual(countdown_parts(naive), countdown_parts(naive.replace(tzinfo=TIMEZONE)))

    def test_aware_datetime_retains_its_instant(self):
        utc_now = datetime(2026, 11, 11, 22, 30, tzinfo=timezone.utc)
        self.assertEqual(countdown_parts(utc_now), (0, 0, 30, 0))
        self.assertEqual(countdown_parts(utc_now), countdown_parts(utc_now.astimezone(TIMEZONE)))

    def test_daylight_saving_change_uses_elapsed_seconds(self):
        # Budapest moves from UTC+2 to UTC+1 before the November meeting.
        now = datetime(2026, 10, 7, tzinfo=TIMEZONE)
        self.assertEqual(countdown_parts(now), (36, 1, 0, 0))


class TimelineTests(unittest.TestCase):
    def test_milestones_are_chronological_and_end_at_next_meeting(self):
        dates = [milestone.date for milestone in MILESTONES]
        self.assertEqual(dates, sorted(dates))
        self.assertEqual(dates[0], FIRST_MEMORY)
        self.assertEqual(dates[-1], NEXT_MEETING)
        self.assertEqual(MILESTONES[-1].label, "Eurotrip")
        self.assertEqual(NEXT_MEETING, datetime(2026, 11, 12, tzinfo=TIMEZONE))

    def test_progress_clamps_before_and_after(self):
        self.assertEqual(timeline_progress(FIRST_MEMORY - timedelta(days=1)), 0.0)
        self.assertEqual(timeline_progress(FIRST_MEMORY), 0.0)
        self.assertEqual(timeline_progress(NEXT_MEETING), 1.0)
        self.assertEqual(timeline_progress(NEXT_MEETING + timedelta(days=1)), 1.0)

    def test_progress_at_midpoint(self):
        start = FIRST_MEMORY.astimezone(timezone.utc)
        end = NEXT_MEETING.astimezone(timezone.utc)
        midpoint = start + (end - start) / 2
        self.assertAlmostEqual(timeline_progress(midpoint), 0.5)

    def test_naive_and_aware_progress_match(self):
        naive = datetime(2026, 10, 7, 12)
        self.assertEqual(timeline_progress(naive), timeline_progress(naive.replace(tzinfo=TIMEZONE)))

    def test_plane_reaches_each_evenly_spaced_stop_on_its_date(self):
        for index, milestone in enumerate(MILESTONES):
            with self.subTest(milestone=milestone):
                self.assertAlmostEqual(route_position(milestone.date), index / 5)

    def test_current_plane_is_between_reencounter_and_eurotrip(self):
        position = route_position(datetime(2026, 10, 7, tzinfo=TIMEZONE))
        self.assertGreater(position, 4 / 5)
        self.assertLess(position, 1.0)

    def test_route_position_clamps_before_and_after(self):
        self.assertEqual(route_position(FIRST_MEMORY - timedelta(days=1)), 0.0)
        self.assertEqual(route_position(NEXT_MEETING + timedelta(days=1)), 1.0)


class CityTests(unittest.TestCase):
    def test_coordinate_hemispheres(self):
        self.assertEqual(formatted_coordinates("Monterrey"), "25.6866° N · 100.3161° O")
        self.assertEqual(formatted_coordinates("Paris"), "48.8566° N · 2.3522° E")

    def test_city_keys_preserve_photo_folder_names(self):
        self.assertEqual(list(CITIES), ["Praga", "Paris", "Monterrey"])
        self.assertEqual(CITIES["Paris"]["label"], "París")


if __name__ == "__main__":
    unittest.main()
