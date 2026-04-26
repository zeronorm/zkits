from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from zkits.utils import ApiResult, cache_with_retry


class UtilsTests(unittest.TestCase):
    def test_cache_with_retry_caches_successful_result(self) -> None:
        with tempfile.TemporaryDirectory() as cache_root:
            with mock.patch.dict(os.environ, {"API_CACHE_ROOT": cache_root}):
                calls = {"count": 0}

                @cache_with_retry(cache_dir="api", expire=60, max_retries=0)
                def fetch_value(value: int) -> ApiResult:
                    calls["count"] += 1
                    return ApiResult(code=0, data=value)

                first = fetch_value(1)
                second = fetch_value(1)

        self.assertEqual(calls["count"], 1)
        self.assertEqual(first.data, 1)
        self.assertFalse(first.is_cached)
        self.assertEqual(second.data, 1)
        self.assertTrue(second.is_cached)

    def test_cache_with_retry_retries_business_failures(self) -> None:
        with tempfile.TemporaryDirectory() as cache_root:
            with mock.patch.dict(os.environ, {"API_CACHE_ROOT": cache_root}):
                calls = {"count": 0}

                @cache_with_retry(
                    cache_dir="api",
                    expire=60,
                    max_retries=1,
                    retry_interval=0,
                )
                def fetch_value() -> ApiResult:
                    calls["count"] += 1
                    if calls["count"] == 1:
                        return ApiResult(code=1, msg="try again")
                    return ApiResult(code=0, data="ok")

                result = fetch_value()

        self.assertEqual(calls["count"], 2)
        self.assertTrue(result.success)
        self.assertEqual(result.data, "ok")


if __name__ == "__main__":
    unittest.main()
