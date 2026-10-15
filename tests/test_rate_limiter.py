from services.rateLimiter import canAllowRequest
import time
import freezegun
from unittest.mock import patch
# import time_machine


def test_rate_limiter_forbid():
    time.sleep(61)
    assert canAllowRequest("test_forbid") == True
    assert canAllowRequest("test_forbid") == True
    assert canAllowRequest("test_forbid") == True
    assert canAllowRequest("test_forbid") == True
    assert canAllowRequest("test_forbid") == True
    # assert canAllowRequest("test") == True
    # assert canAllowRequest("test") == True
    assert canAllowRequest("test_forbid") == False
    # time.sleep(61)

# @freezegun.freeze_time("2026-10-13 12:00:00", tick=True)
# @patch("time.sleep", return_value=None) # Overrides sleep so it takes 0 seconds
def test_rate_limiter_allow():
    time.sleep(61)
    assert canAllowRequest("test_allow") == True
    assert canAllowRequest("test_allow") == True
    assert canAllowRequest("test_allow") == True
    assert canAllowRequest("test_allow") == True
    assert canAllowRequest("test_allow") == True
    time.sleep(61)
    assert canAllowRequest("test_allow") == True
    # time.sleep(61)
