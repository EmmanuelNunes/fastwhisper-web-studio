import pytest
import os
import sys

# Garante import do modulo core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils import format_timestamp, get_device_info, check_ffmpeg_available

def test_format_timestamp_seconds():
    assert format_timestamp(45.2) == "[00:00:45]"

def test_format_timestamp_minutes():
    assert format_timestamp(135.8) == "[00:02:15]"

def test_format_timestamp_hours():
    assert format_timestamp(3672.0) == "[01:01:12]"

def test_format_timestamp_zero():
    assert format_timestamp(0) == "[00:00:00]"

def test_get_device_info():
    info = get_device_info()
    assert isinstance(info, dict)
    assert "device" in info
    assert "compute_type" in info
    assert info["device"] in ["cuda", "cpu"]
    assert info["compute_type"] in ["float16", "int8_float16", "int8"]

def test_check_ffmpeg_available():
    # Ja verificamos que o ffmpeg esta no PATH do Windows
    available = check_ffmpeg_available()
    assert available is True
