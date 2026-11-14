import pytest
from src.monitoring.retry import run_with_retry


def test_retry_succeeds_after_transient_failure():
    calls = {"count": 0}
    def operation():
        calls["count"] += 1
        if calls["count"] < 2:
            raise RuntimeError("temporary")
        return "ok"
    assert run_with_retry(operation, attempts=2, base_delay_seconds=0) == "ok"
    assert calls["count"] == 2


def test_retry_reraises_after_final_attempt():
    def operation():
        raise ValueError("permanent")
    with pytest.raises(ValueError):
        run_with_retry(operation, attempts=2, base_delay_seconds=0)
