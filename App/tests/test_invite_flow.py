from database.email_contacts import add_contact, get_contact_by_email
from database.password_reset import create_reset_token, get_reset_token, consume_reset_token
from database.users import get_user_by_username, add_user


def test_invite_token_creates_user():
    # Crear contacto sin usuario asociado
    email = "newperson@example.com"
    add_contact(email, name="New Person")
    contact = get_contact_by_email(email)
    assert contact

    # Crear token de invitación
    token = create_reset_token(user_id=None, email=email)
    row = get_reset_token(token)
    assert row is not None
    assert row.get("email") == email
    assert row.get("user_id") in (0, None)

    # Simular que el usuario crea su cuenta usando el email
    username = "newperson"
    assert not get_user_by_username(username)
    add_user(username, "pass123", role="user", email=email)

    # Consumir token
    consume_reset_token(token)
    row2 = get_reset_token(token)
    assert row2 is not None
    assert row2.get("used")

    # Ahora el usuario existe
    u = get_user_by_username(username)
    assert u and u.get("email") == email
