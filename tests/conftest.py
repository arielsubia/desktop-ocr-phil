"""Shared test fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_app_data(tmp_path, monkeypatch):
    """Point app data at a temp dir so tests never touch real user settings."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    yield


@pytest.fixture(autouse=True)
def _mock_aws_credentials(monkeypatch):
    """Provide dummy AWS credentials so boto3 imports never hit real config."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    yield


@pytest.fixture
def _clear_localappdata(monkeypatch):
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    yield
