import json
from typing import Iterator, Union

import pytest
from starlette.testclient import TestClient

from stac_fastapi.api.app import StacApi
from stac_fastapi.extensions.core import TransactionExtension
from stac_fastapi.types.config import ApiSettings
from stac_fastapi.types.core import BaseCoreClient, BaseTransactionsClient
from stac_fastapi.types.stac import Collection, Item, ItemCollection


class DummyCoreClient(BaseCoreClient):
    def all_collections(self, *args, **kwargs):
        raise NotImplementedError

    def get_collection(self, *args, **kwargs):
        raise NotImplementedError

    def get_item(self, *args, **kwargs):
        raise NotImplementedError

    def get_search(self, *args, **kwargs):
        raise NotImplementedError

    def post_search(self, *args, **kwargs):
        raise NotImplementedError

    def item_collection(self, *args, **kwargs):
        raise NotImplementedError


class DummyTransactionsClient(BaseTransactionsClient):
    """Dummy client returning parts of the request, rather than proper STAC items."""

    def create_item(self, item: Union[Item, ItemCollection], **kwargs):
        return {"type": item["type"]}

    def update_item(self, collection_id: str, item_id: str, item: Item, **kwargs):
        return {
            "path_collection_id": collection_id,
            "path_item_id": item_id,
            "type": item["type"],
        }

    def delete_item(self, item_id: str, collection_id: str, **kwargs):
        return {
            "path_collection_id": collection_id,
            "path_item_id": item_id,
        }

    def create_collection(self, collection: Collection, **kwargs):
        return {"type": collection["type"]}

    def update_collection(self, collection_id: str, collection: Collection, **kwargs):
        return {"path_collection_id": collection_id, "type": collection["type"]}

    def delete_collection(self, collection_id: str, **kwargs):
        return {"path_collection_id": collection_id}


@pytest.mark.skip(reason="Database is readonly")
def test_create_item(client: TestClient, item: Item) -> None:
    response = client.post("/collections/a-collection/items", content=json.dumps(item))
    assert response.is_success, response.text
    assert response.json()["type"] == "Feature"


@pytest.mark.skip(reason="Database is readonly")
def test_create_item_collection(
    client: TestClient, item_collection: ItemCollection
) -> None:
    response = client.post(
        "/collections/a-collection/items", content=json.dumps(item_collection)
    )
    assert response.is_success, response.text
    assert response.json()["type"] == "FeatureCollection"


@pytest.mark.skip(reason="Database is readonly")
def test_update_item(client: TestClient, item: Item) -> None:
    response = client.put(
        "/collections/a-collection/items/an-item", content=json.dumps(item)
    )
    assert response.is_success, response.text
    assert response.json()["path_collection_id"] == "a-collection"
    assert response.json()["path_item_id"] == "an-item"
    assert response.json()["type"] == "Feature"


@pytest.mark.skip(reason="Database is readonly")
def test_delete_item(client: TestClient) -> None:
    response = client.delete("/collections/a-collection/items/an-item")
    assert response.is_success, response.text
    assert response.json()["path_collection_id"] == "a-collection"
    assert response.json()["path_item_id"] == "an-item"


@pytest.mark.skip(reason="Database is readonly")
def test_create_collection(client: TestClient, collection: Collection) -> None:
    response = client.post("/collections", content=json.dumps(collection))
    assert response.is_success, response.text
    assert response.json()["type"] == "Collection"


@pytest.mark.skip(reason="Database is readonly")
def test_update_collection(client: TestClient, collection: Collection) -> None:
    response = client.put("/collections/a-collection", content=json.dumps(collection))
    assert response.is_success, response.text
    assert response.json()["path_collection_id"] == "a-collection"
    assert response.json()["type"] == "Collection"


@pytest.mark.skip(reason="Database is readonly")
def test_delete_collection(client: TestClient, collection: Collection) -> None:
    response = client.delete("/collections/a-collection")
    assert response.is_success, response.text
    assert response.json()["path_collection_id"] == "a-collection"


@pytest.fixture
def client(
    core_client: DummyCoreClient, transactions_client: DummyTransactionsClient
) -> Iterator[TestClient]:
    settings = ApiSettings()
    api = StacApi(
        settings=settings,
        client=core_client,
        extensions=[
            TransactionExtension(client=transactions_client, settings=settings),
        ],
    )
    with TestClient(api.app) as client:
        yield client


@pytest.fixture
def core_client() -> DummyCoreClient:
    return DummyCoreClient()


@pytest.fixture
def transactions_client() -> DummyTransactionsClient:
    return DummyTransactionsClient()


@pytest.fixture
def item_collection(item: Item) -> ItemCollection:
    return {
        "type": "FeatureCollection",
        "features": [item],
        "links": [],
        "context": None,
    }


@pytest.fixture
def item() -> Item:
    return {
        "type": "Feature",
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "test_item",
        "geometry": {"type": "Point", "coordinates": [-105, 40]},
        "bbox": [-105, 40, -105, 40],
        "properties": {},
        "links": [],
        "assets": {},
        "collection": "test_collection",
    }


@pytest.fixture
def collection() -> Collection:
    return {
        "type": "Collection",
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "test_collection",
        "extent": {
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {
                "interval": [["2000-01-01T00:00:00Z", "2024-01-01T00:00:00Z"]]
            },
        },
    }
