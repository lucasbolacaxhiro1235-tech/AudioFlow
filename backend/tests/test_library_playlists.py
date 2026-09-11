import uuid

from tests.helpers import insert_download, insert_file


async def _visitor_id(client, headers):
    return (await client.get("/api/me", headers=headers)).json()["id"]


async def test_library_and_playlist_crud(client, visitor_a):
    uid = await _visitor_id(client, visitor_a)

    fid = await insert_file(uid)
    await insert_download(uid)

    r = await client.get("/api/library", headers=visitor_a)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 1
    target = next(i for i in items if i["id"] == str(fid))
    assert target["metadata"]["title"] == "Faixa Teste"
    assert target["download_url"] is not None

    r = await client.post("/api/playlists", headers=visitor_a, json={"name": "Minha"})
    assert r.status_code == 201
    pid = r.json()["id"]

    r = await client.post(f"/api/playlists/{pid}/items", headers=visitor_a, json={"file_id": str(fid)})
    assert r.status_code == 200
    assert r.json()["track_count"] == 1

    r = await client.get(f"/api/playlists/{pid}", headers=visitor_a)
    assert r.json()["track_count"] == 1

    item_id = r.json()["items"][0]["id"]
    r = await client.put(f"/api/playlists/{pid}/items/reorder", headers=visitor_a, json=[str(item_id)])
    assert r.status_code == 200

    r = await client.delete(f"/api/playlists/{pid}/items/{item_id}", headers=visitor_a)
    assert r.status_code == 200
    assert r.json()["track_count"] == 0

    r = await client.put(f"/api/playlists/{pid}", headers=visitor_a, json={"name": "Renomeada"})
    assert r.json()["name"] == "Renomeada"
    r = await client.delete(f"/api/playlists/{pid}", headers=visitor_a)
    assert r.status_code == 200


async def test_library_delete(client, visitor_a):
    uid = await _visitor_id(client, visitor_a)
    fid = await insert_file(uid)

    r = await client.delete(f"/api/library/{fid}", headers=visitor_a)
    assert r.status_code == 200

    r = await client.get(f"/api/library/{fid}", headers=visitor_a)
    assert r.status_code == 404


async def test_file_not_found(client, visitor_a):
    r = await client.get("/api/library/00000000-0000-0000-0000-000000000000", headers=visitor_a)
    assert r.status_code == 404


async def test_add_duplicate_playlist_item(client, visitor_a):
    uid = await _visitor_id(client, visitor_a)
    fid = await insert_file(uid, title=f"Dup {uuid.uuid4()}")
    r = await client.post("/api/playlists", headers=visitor_a, json={"name": "Dup"})
    pid = r.json()["id"]
    await client.post(f"/api/playlists/{pid}/items", headers=visitor_a, json={"file_id": str(fid)})
    r = await client.post(f"/api/playlists/{pid}/items", headers=visitor_a, json={"file_id": str(fid)})
    assert r.status_code == 409