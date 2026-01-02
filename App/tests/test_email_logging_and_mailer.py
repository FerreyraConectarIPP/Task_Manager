import utils.mailer as mailer
from database.emails import log_email, get_logs

class DummySMTP:
    def __init__(self, server, port, timeout=None):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def starttls(self):
        pass
    def login(self, user, password):
        pass
    def send_message(self, msg):
        # pretend to send
        pass

class FailSMTP(DummySMTP):
    def send_message(self, msg):
        raise RuntimeError("network error")


def test_log_email_and_get_logs():
    # Log an email and verify get_logs returns it
    log_email("x@example.com", "subj", "body", status="sent")
    rows = get_logs(limit=10)
    assert any(r["to_email"] == "x@example.com" and r["status"] == "sent" for r in rows)


def test_send_reset_email_success(monkeypatch, tmp_path):
    # Ensure mailer uses a fake SMTP that succeeds
    monkeypatch.setattr(mailer, "SMTP_SERVER", "smtp.test")
    monkeypatch.setattr(mailer.smtplib, "SMTP", DummySMTP)

    ok, msg = mailer.send_reset_email("ok@test.com", "tester", "http://example/?t=1")
    assert ok
    rows = get_logs(limit=10)
    assert any(r["to_email"] == "ok@test.com" and r["status"] == "sent" for r in rows)


def test_send_reset_email_failure_logs(monkeypatch):
    monkeypatch.setattr(mailer, "SMTP_SERVER", "smtp.test")
    monkeypatch.setattr(mailer.smtplib, "SMTP", FailSMTP)

    ok, msg = mailer.send_reset_email("fail@test.com", "tester", "http://example/?t=1")
    assert not ok
    rows = get_logs(limit=10)
    assert any(r["to_email"] == "fail@test.com" and r["status"] == "failed" for r in rows)
