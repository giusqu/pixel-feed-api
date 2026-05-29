import pytest

from src.config import TestConfig, config


@pytest.mark.anyio
async def test_config_is_test():
    assert isinstance(config, TestConfig)
