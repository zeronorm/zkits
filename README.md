# zkit

`zkit` is a foundational Python toolkit that bundles reusable library code and command-line utilities.

## Install

For local development:

```bash
python -m pip install -e .
```

From PyPI:

```bash
python -m pip install zkits
```

## Library Usage

```python
from zkit import check_env

info = check_env()
print(info["python_version"])
```

```python
from zkit.utils import ApiResult, cache_with_retry

@cache_with_retry(cache_dir="quotes", expire=300, max_retries=2)
def fetch_quote(symbol: str) -> ApiResult:
    return ApiResult(code=0, data={"symbol": symbol, "price": 100})

result = fetch_quote("AAPL")
print(result.success, result.is_cached)
```

## CLI Usage

```bash
zkit check_env
```

Use JSON output when another tool needs to parse the result:

```bash
zkit check_env --json
```

## Development

```bash
python -m unittest discover -s tests -v
```
