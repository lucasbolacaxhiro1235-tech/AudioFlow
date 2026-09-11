import pytest



async def test_me_returns_visitor(client, visitor_a):
    r = await client.get("/api/me", headers=visitor_a)
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Visitante"
    assert body["role"] == "user"
    assert body["id"]


async def test_visitor_isolation(client, visitor_a, visitor_b):
    a = (await client.get("/api/me", headers=visitor_a)).json()
    b = (await client.get("/api/me", headers=visitor_b)).json()
    assert a["id"] != b["id"]

    # visitor A creates a playlist
    r = await client.post("/api/playlists", headers=visitor_a, json={"name": "Playlist A"})
    assert r.status_code == 201
    pid_a = r.json()["id"]

    r = await client.post("/api/playlists", headers=visitor_b, json={"name": "Playlist B"})
    assert r.status_code == 201
    pid_b = r.json()["id"]

    # visitor A sees only its own
    a_playlists = (await client.get("/api/playlists", headers=visitor_a)).json()
    b_playlists = (await client.get("/api/playlists", headers=visitor_b)).json()
    a_ids = {p["id"] for p in a_playlists}
    b_ids = {p["id"] for p in b_playlists}
    assert pid_a in a_ids and pid_b not in a_ids
    assert pid_b in b_ids and pid_a not in b_ids

    # cross access is forbidden
    r = await client.get(f"/api/playlists/{pid_a}", headers=visitor_b)
    assert r.status_code == 404


async def test_same_client_id_persistent(client, fresh_client):
    r1 = (await client.get("/api/me", headers=fresh_client)).json()
    r2 = (await client.get("/api/me", headers=fresh_client)).json()
    assert r1["id"] == r2["id"]


async def test_no_client_id_authenticates_as_anonymous(client):
    # With ALLOW_ANONYMOUS, no header -> 401 (guest needs client id)
    r = await client.get("/api/me")
    assert r.status_code == 401