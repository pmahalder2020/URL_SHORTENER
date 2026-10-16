import unittest
from unittest.mock import patch

import rate_limiter


class TestSlidingWindowRateLimiter(unittest.TestCase):
    def setUp(self):
        rate_limiter.request_log.clear()

    @patch("rate_limiter.time.time")
    def test_allows_requests_up_to_the_limit(self, mock_time):
        mock_time.return_value = 1000.0
        for _ in range(5):
            self.assertTrue(rate_limiter.is_allowed("1.1.1.1", 5, 60))

    @patch("rate_limiter.time.time")
    def test_blocks_request_over_the_limit(self, mock_time):
        mock_time.return_value = 1000.0
        for _ in range(5):
            rate_limiter.is_allowed("1.1.1.1", 5, 60)
        self.assertFalse(rate_limiter.is_allowed("1.1.1.1", 5, 60))

    @patch("rate_limiter.time.time")
    def test_blocked_requests_are_not_recorded(self, mock_time):
        mock_time.return_value = 1000.0
        for _ in range(8):
            rate_limiter.is_allowed("1.1.1.1", 5, 60)
        self.assertEqual(len(rate_limiter.request_log["1.1.1.1"]), 5)

    @patch("rate_limiter.time.time")
    def test_requests_allowed_again_after_window_passes(self, mock_time):
        mock_time.return_value = 1000.0
        for _ in range(5):
            rate_limiter.is_allowed("1.1.1.1", 5, 60)
        self.assertFalse(rate_limiter.is_allowed("1.1.1.1", 5, 60))

        mock_time.return_value = 1061.0  # window has fully passed
        self.assertTrue(rate_limiter.is_allowed("1.1.1.1", 5, 60))

    @patch("rate_limiter.time.time")
    def test_window_slides_instead_of_resetting(self, mock_time):
        # 3 requests at t=1000, 2 requests at t=1030
        mock_time.return_value = 1000.0
        for _ in range(3):
            rate_limiter.is_allowed("1.1.1.1", 5, 60)
        mock_time.return_value = 1030.0
        for _ in range(2):
            rate_limiter.is_allowed("1.1.1.1", 5, 60)
        self.assertFalse(rate_limiter.is_allowed("1.1.1.1", 5, 60))

        # At t=1061 the first 3 have expired but the 2 from t=1030 remain,
        # so exactly 3 more requests fit.
        mock_time.return_value = 1061.0
        for _ in range(3):
            self.assertTrue(rate_limiter.is_allowed("1.1.1.1", 5, 60))
        self.assertFalse(rate_limiter.is_allowed("1.1.1.1", 5, 60))

    @patch("rate_limiter.time.time")
    def test_each_ip_is_limited_independently(self, mock_time):
        mock_time.return_value = 1000.0
        for _ in range(5):
            rate_limiter.is_allowed("1.1.1.1", 5, 60)
        self.assertFalse(rate_limiter.is_allowed("1.1.1.1", 5, 60))
        self.assertTrue(rate_limiter.is_allowed("2.2.2.2", 5, 60))


if __name__ == "__main__":
    unittest.main()
