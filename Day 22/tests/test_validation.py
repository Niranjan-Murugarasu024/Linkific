import pandas as pd
import pytest
from src.validation.data_quality import validate_required_columns, validate_no_nulls

def test_required_columns_pass():
    assert validate_required_columns(pd.DataFrame({"id": [1]}), ["id"])

def test_required_columns_fail():
    with pytest.raises(ValueError):
        validate_required_columns(pd.DataFrame({"id": [1]}), ["id", "name"])

def test_nulls_fail():
    with pytest.raises(ValueError):
        validate_no_nulls(pd.DataFrame({"id": [1, None]}), ["id"])
