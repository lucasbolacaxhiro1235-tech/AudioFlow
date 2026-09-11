from app.core.security import hash_password, verify_password


def test_password_hash_argon2():
    hashed = hash_password("S3nh@Forte123")
    assert hashed.startswith("$argon2")
    assert verify_password("S3nh@Forte123", hashed)
    assert not verify_password("errada", hashed)


async def test_register_login_flow(client):
    email = "user1@example.com"
    r = await client.post(
        "/api/auth/register",
        json={"email": email, "name": "Usuário Um", "password": "S3nh@Forte123"},
        headers={"X-Client-Id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc"},
    )
    assert r.status_code in (200, 201)

    r = await client.post(
        "/api/auth/register",
        json={"email": email, "name": "Outro", "password": "S3nh@Forte123"},
        headers={"X-Client-Id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc"},
    )
    assert r.status_code == 409

    r = await client.post("/api/auth/login", json={"email": email, "password": "S3nh@Forte123"})
    assert r.status_code == 200
    token = r.json()
    assert "access_token" in token

    r = await client.post("/api/auth/login", json={"email": email, "password": "senhaerrada"})
    assert r.status_code == 401

    r = await client.get("/api/me", headers={"Authorization": f"Bearer {token['access_token']}"})
    assert r.status_code == 200
    assert r.json()["email"] == email


async def test_login_wrong_password(client):
    r = await client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "x" * 10})
    assert r.status_code == 401