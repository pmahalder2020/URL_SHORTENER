import os
import tempfile
import unittest

import db
import rate_limiter

# Point the database at a throwaway file BEFORE importing the app,
# so tests never touch the real shortener.db.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
db.DB_FILE = _tmp.name

import app as app_module  # noqa: E402


class TestShortenerAPI(unittest.TestCase):
    def setUp(self):
        # Fresh empty table and fresh rate-limit state for every test
        conn = db.get_connection()
        conn.execute("DROP TABLE IF EXISTS urls")
        conn.commit()
        conn.close()
        db.init_db()
        rate_limiter.request_log.clear()
        self.client = app_module.app.test_client()

    @classmethod
    def tearDownClass(cls):
        os.unlink(_tmp.name)

    def _shorten(self, url="https://example.com/some/long/path"):
        return self.client.post("/shorten", json={"url": url})

    # ---- POST /shorten ----
    def test_shorten_valid_url_returns_201_and_code(self):
        res = self._shorten()
        self.assertEqual(res.status_code, 201)
        body = res.get_json()
        self.assertEqual(body["short_code"], "1")  # first row id is 1
        self.assertEqual(body["long_url"], "https://example.com/some/long/path")
        self.assertTrue(body["short_url"].endswith("/1"))

    def test_shorten_gives_unique_codes_for_each_url(self):
        codes = {self._shorten(f"https://example.com/{i}").get_json()["short_code"]
                 for i in range(4)}
        self.assertEqual(len(codes), 4)

    def test_shorten_missing_url_returns_400(self):
        res = self.client.post("/shorten", json={})
        self.assertEqual(res.status_code, 400)

    def test_shorten_with_no_json_body_returns_400(self):
        res = self.client.post("/shorten", data="not json")
        self.assertEqual(res.status_code, 400)

    def test_shorten_rejects_url_without_http_scheme(self):
        for bad in ("example.com", "ftp://example.com", "javascript:alert(1)"):
            with self.subTest(url=bad):
                rate_limiter.request_log.clear()
                self.assertEqual(self._shorten(bad).status_code, 400)

    def test_shorten_is_rate_limited_after_five_requests(self):
        statuses = [self._shorten(f"https://example.com/{i}").status_code for i in range(6)]
        self.assertEqual(statuses, [201, 201, 201, 201, 201, 429])

    # ---- GET /<short_code> ----
    def test_redirect_returns_302_to_original_url(self):
        code = self._shorten("https://example.com/target").get_json()["short_code"]
        res = self.client.get(f"/{code}")
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.headers["Location"], "https://example.com/target")

    def test_redirect_unknown_code_returns_404(self):
        res = self.client.get("/zzzz")
        self.assertEqual(res.status_code, 404)

    def test_redirect_invalid_characters_returns_404(self):
        res = self.client.get("/bad$code")
        self.assertEqual(res.status_code, 404)

    # ---- GET /stats/<short_code> ----
    def test_stats_starts_at_zero_clicks(self):
        code = self._shorten().get_json()["short_code"]
        body = self.client.get(f"/stats/{code}").get_json()
        self.assertEqual(body["clicks"], 0)
        self.assertEqual(body["long_url"], "https://example.com/some/long/path")

    def test_each_redirect_increments_click_count(self):
        code = self._shorten().get_json()["short_code"]
        for _ in range(3):
            self.client.get(f"/{code}")
        self.assertEqual(self.client.get(f"/stats/{code}").get_json()["clicks"], 3)

    def test_viewing_stats_does_not_count_as_a_click(self):
        code = self._shorten().get_json()["short_code"]
        self.client.get(f"/stats/{code}")
        self.client.get(f"/stats/{code}")
        self.assertEqual(self.client.get(f"/stats/{code}").get_json()["clicks"], 0)

    def test_stats_unknown_code_returns_404(self):
        self.assertEqual(self.client.get("/stats/zzzz").status_code, 404)

    # ---- GET / ----
    def test_home_returns_running_message(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("running", res.get_json()["message"])


if __name__ == "__main__":
    unittest.main()
