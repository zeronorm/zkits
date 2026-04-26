"""General-purpose utilities for zkits."""

from __future__ import annotations

import functools
import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar, cast

import diskcache

logger = logging.getLogger("CacheWrapper")
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


@dataclass
class ApiResult:
    code: int
    msg: str = ""
    data: Any = None
    is_cached: bool = False

    @property
    def success(self) -> bool:
        return self.code == 0


RT = TypeVar("RT", bound=ApiResult)


def cache_with_retry(
    cache_dir: str = "default_api",
    expire: int = 300,
    max_retries: int = 3,
    retry_interval: float = 1.0,
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """Cache successful API-style results and retry failed calls.

    The decorated function is expected to return an ``ApiResult`` or subclass.
    Only successful results, where ``result.success`` is true, are cached.
    """

    if max_retries < 0:
        raise ValueError("max_retries must be greater than or equal to 0")
    if retry_interval < 0:
        raise ValueError("retry_interval must be greater than or equal to 0")

    root_dir = os.getenv("API_CACHE_ROOT", "./cache")
    full_cache_path = os.path.join(root_dir, cache_dir)
    cache = diskcache.Cache(full_cache_path)

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> RT:
            func_name = func.__name__
            raw_key = (func_name, args, tuple(sorted(kwargs.items())))
            log_key = f"{func_name}_{hash(str(raw_key))}"

            try:
                cached_result = cache.get(raw_key)
                if cached_result is not None:
                    cached_result.is_cached = True
                    logger.info(
                        "[CacheWrapper] status=HIT_CACHE | func=%s | key=%s | "
                        "attempt=0/%s | msg=命中缓存",
                        func_name,
                        log_key,
                        max_retries,
                    )
                    return cast(RT, cached_result)
            except Exception as exc:
                logger.warning(
                    "[CacheWrapper] status=CACHE_READ_ERR | func=%s | key=%s | "
                    "attempt=0/%s | msg=读缓存异常: %s",
                    func_name,
                    log_key,
                    max_retries,
                    exc,
                )

            last_exception: Exception | None = None
            last_result: RT | None = None

            for attempt in range(1, max_retries + 2):
                try:
                    result = func(*args, **kwargs)
                    last_result = result

                    if isinstance(result, ApiResult) and result.success:
                        result.is_cached = False

                        try:
                            cache.set(raw_key, result, expire=expire)
                            cache_status = "CACHE_WRITE_OK"
                        except Exception as exc:
                            cache_status = "CACHE_WRITE_ERR"
                            logger.error(
                                "[CacheWrapper] status=%s | func=%s | key=%s | "
                                "attempt=%s/%s | msg=写缓存异常: %s",
                                cache_status,
                                func_name,
                                log_key,
                                attempt,
                                max_retries,
                                exc,
                            )

                        logger.info(
                            "[CacheWrapper] status=API_SUCCESS | func=%s | key=%s | "
                            "attempt=%s/%s | msg=执行成功, %s",
                            func_name,
                            log_key,
                            attempt,
                            max_retries,
                            cache_status,
                        )
                        return result

                    biz_code = getattr(result, "code", "unknown")
                    logger.warning(
                        "[CacheWrapper] status=API_FAIL | func=%s | key=%s | "
                        "attempt=%s/%s | msg=业务返回失败(code=%s)",
                        func_name,
                        log_key,
                        attempt,
                        max_retries,
                        biz_code,
                    )
                except Exception as exc:
                    last_exception = exc
                    err_msg = str(exc).replace("\n", " ")
                    logger.error(
                        "[CacheWrapper] status=API_EXCEPTION | func=%s | key=%s | "
                        "attempt=%s/%s | msg=抛出异常: %s",
                        func_name,
                        log_key,
                        attempt,
                        max_retries,
                        err_msg,
                    )

                if attempt <= max_retries:
                    time.sleep(retry_interval)

            logger.error(
                "[CacheWrapper] status=ALL_FAILED | func=%s | key=%s | "
                "attempt=%s/%s | msg=达到最大重试次数",
                func_name,
                log_key,
                max_retries + 1,
                max_retries,
            )
            if last_exception:
                raise last_exception
            return cast(RT, last_result)

        return wrapper

    return decorator
