from datetime import datetime, timedelta
from database.password_reset import create_reset_token, get_reset_token, consume_reset_token, cleanup_expired_tokens


def test_create_and_consume_token():
    token = create_reset_token(user_id=1, expiry_minutes=60)
    row = get_reset_token(token)
    assert row is not None
    assert row["used"] is False or row["used"] == 0

    consume_reset_token(token)
    row2 = get_reset_token(token)
    assert row2 is not None
    assert row2["used"] == 1


def test_expired_token_cleanup():
    token = create_reset_token(user_id=2, expiry_minutes=-1)
    row = get_reset_token(token)
    # token exists but is expired; cleanup should remove it
    cleanup_expired_tokens()
    row2 = get_reset_token(token)
    assert row2 is None
