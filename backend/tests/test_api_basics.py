

async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


async def test_plans_list(client):
    r = await client.get("/api/plans")
    assert r.status_code == 200
    tiers = {p["tier"] for p in r.json()}
    assert tiers == {"free", "pro", "premium"}


async def test_invalid_url_rejected(client, visitor_a):
    r = await client.post("/api/downloads", headers=visitor_a, json={"url": "batata", "format": "mp3"})
    assert r.status_code in (422, 400)


async def test_empty_url_rejected(client, visitor_a):
    r = await client.post("/api/downloads", headers=visitor_a, json={"url": "", "format": "mp3"})
    assert r.status_code == 422


async def test_invalid_format_rejected(client, visitor_a):
    r = await client.post(
        "/api/downloads",
        headers=visitor_a,
        json={"url": "https://example.com/track", "format": "exe"},
    )
    assert r.status_code == 422


async def test_download_not_found(client, visitor_a):
    r = await client.get("/api/downloads/00000000-0000-0000-0000-000000000000", headers=visitor_a)
    assert r.status_code == 404


async def test_library_empty(client, visitor_a):
    r = await client.get("/api/library", headers=visitor_a)
    assert r.status_code == 200
    assert r.json()["total"] == 0


async def test_admin_forbidden_for_guest(client, visitor_a):
    r = await client.get("/api/admin/stats", headers=visitor_a)
    assert r.status_code == 403