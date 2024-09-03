"""Base clients."""

import abc
from typing import Any, Dict, List, Optional, Union
# from urllib.parse import urljoin

import attr
from fastapi import Request
from stac_pydantic.links import Relations
from stac_pydantic.shared import BBox, MimeTypes
from stac_pydantic.version import STAC_VERSION
from starlette.responses import Response

from stac_fastapi.types import stac as stac_types
from stac_fastapi.types.errors import NotFoundError
from stac_fastapi.types.config import ApiSettings
from stac_fastapi.types.conformance import BASE_CONFORMANCE_CLASSES
from stac_fastapi.types.extension import ApiExtension
from stac_fastapi.types.links import BaseHrefBuilder
# from stac_fastapi.types.requests import get_base_url
from stac_fastapi.types.rfc3339 import DateTimeType
from stac_fastapi.types.search import BaseSearchPostRequest
from stac_fastapi.types.stac import Conformance

NumType = Union[float, int]
StacType = Dict[str, Any]

api_settings = ApiSettings()


@attr.s  # type:ignore
class BaseTransactionsClient(abc.ABC):
    """Defines a pattern for implementing the STAC API Transaction Extension."""

    @abc.abstractmethod
    def create_item(
        self,
        collection_id: str,
        item: Union[stac_types.Item, stac_types.ItemCollection],
        **kwargs,
    ) -> Optional[Union[stac_types.Item, Response, None]]:
        """Create a new item.

        Called with `POST /collections/{collection_id}/items`.

        Args:
            item: the item or item collection
            collection_id: the id of the collection from the resource path

        Returns:
            The item that was created or None if item collection.
        """
        ...

    @abc.abstractmethod
    def update_item(
        self, collection_id: str, item_id: str, item: stac_types.Item, **kwargs
    ) -> Optional[Union[stac_types.Item, Response]]:
        """Perform a complete update on an existing item.

        Called with `PUT /collections/{collection_id}/items`. It is expected
        that this item already exists.  The update should do a diff against the
        saved item and perform any necessary updates.  Partial updates are not
        supported by the transactions extension.

        Args:
            item: the item (must be complete)
            collection_id: the id of the collection from the resource path

        Returns:
            The updated item.
        """
        ...

    @abc.abstractmethod
    def delete_item(
        self, item_id: str, collection_id: str, **kwargs
    ) -> Optional[Union[stac_types.Item, Response]]:
        """Delete an item from a collection.

        Called with `DELETE /collections/{collection_id}/items/{item_id}`

        Args:
            item_id: id of the item.
            collection_id: id of the collection.

        Returns:
            The deleted item.
        """
        ...

    @abc.abstractmethod
    def create_collection(
        self, collection: stac_types.Collection, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Create a new collection.

        Called with `POST /collections`.

        Args:
            collection: the collection

        Returns:
            The collection that was created.
        """
        ...

    @abc.abstractmethod
    def update_collection(
        self, collection_id: str, collection: stac_types.Collection, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Perform a complete update on an existing collection.

        Called with `PUT /collections/{collection_id}`. It is expected that this
        collection already exists.  The update should do a diff against the saved
        collection and perform any necessary updates.  Partial updates are not
        supported by the transactions extension.

        Args:
            collection_id: id of the existing collection to be updated
            collection: the updated collection (must be complete)

        Returns:
            The updated collection.
        """
        ...

    @abc.abstractmethod
    def delete_collection(
        self, collection_id: str, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Delete a collection.

        Called with `DELETE /collections/{collection_id}`

        Args:
            collection_id: id of the collection.

        Returns:
            The deleted collection.
        """
        ...


@attr.s  # type:ignore
class AsyncBaseTransactionsClient(abc.ABC):
    """Defines a pattern for implementing the STAC transaction extension."""

    @abc.abstractmethod
    async def create_item(
        self,
        collection_id: str,
        item: Union[stac_types.Item, stac_types.ItemCollection],
        **kwargs,
    ) -> Optional[Union[stac_types.Item, Response, None]]:
        """Create a new item.

        Called with `POST /collections/{collection_id}/items`.

        Args:
            item: the item or item collection
            collection_id: the id of the collection from the resource path

        Returns:
            The item that was created or None if item collection.
        """
        ...

    @abc.abstractmethod
    async def update_item(
        self, collection_id: str, item_id: str, item: stac_types.Item, **kwargs
    ) -> Optional[Union[stac_types.Item, Response]]:
        """Perform a complete update on an existing item.

        Called with `PUT /collections/{collection_id}/items`. It is expected
        that this item already exists.  The update should do a diff against the
        saved item and perform any necessary updates.  Partial updates are not
        supported by the transactions extension.

        Args:
            item: the item (must be complete)

        Returns:
            The updated item.
        """
        ...

    @abc.abstractmethod
    async def delete_item(
        self, item_id: str, collection_id: str, **kwargs
    ) -> Optional[Union[stac_types.Item, Response]]:
        """Delete an item from a collection.

        Called with `DELETE /collections/{collection_id}/items/{item_id}`

        Args:
            item_id: id of the item.
            collection_id: id of the collection.

        Returns:
            The deleted item.
        """
        ...

    @abc.abstractmethod
    async def create_collection(
        self, collection: stac_types.Collection, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Create a new collection.

        Called with `POST /collections`.

        Args:
            collection: the collection

        Returns:
            The collection that was created.
        """
        ...

    @abc.abstractmethod
    async def update_collection(
        self, collection_id: str, collection: stac_types.Collection, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Perform a complete update on an existing collection.

        Called with `PUT /collections/{collection_id}`. It is expected that this item
        already exists.  The update should do a diff against the saved collection and
        perform any necessary updates.  Partial updates are not supported by the
        transactions extension.

        Args:
            collection_id: id of the existing collection to be updated
            collection: the updated collection (must be complete)

        Returns:
            The updated collection.
        """
        ...

    @abc.abstractmethod
    async def delete_collection(
        self, collection_id: str, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Delete a collection.

        Called with `DELETE /collections/{collection_id}`

        Args:
            collection_id: id of the collection.

        Returns:
            The deleted collection.
        """
        ...


@attr.s
class LandingPageMixin(abc.ABC):
    """Create a STAC landing page (GET /)."""

    stac_version: str = attr.ib(default=STAC_VERSION)
    landing_page_id: str = attr.ib(default=api_settings.stac_fastapi_landing_id)
    title: str = attr.ib(default=api_settings.stac_fastapi_title)
    description: str = attr.ib(default=api_settings.stac_fastapi_description)

    def _landing_page(
        self,
        # base_url: str,
        href_builder: BaseHrefBuilder,
        conformance_classes: List[str],
        extension_schemas: List[str],
    ) -> stac_types.LandingPage:
        landing_page = stac_types.LandingPage(
            type="Catalog",
            id=self.landing_page_id,
            title=self.title,
            description=self.description,
            stac_version=self.stac_version,
            conformsTo=conformance_classes,
            links=[
                {
                    "rel": Relations.self.value,
                    "type": MimeTypes.json,
                    # "href": base_url,
                    "href": href_builder.build("./"),
                },
                {
                    "rel": Relations.root.value,
                    "type": MimeTypes.json,
                    # "href": base_url,
                    "href": href_builder.build("./"),
                },
                {
                    "rel": "data",
                    "type": MimeTypes.json,
                    # "href": urljoin(base_url, "collections"),
                    "href": href_builder.build("collections"),
                },
                {
                    "rel": Relations.conformance.value,
                    "type": MimeTypes.json,
                    "title": "STAC/OGC conformance classes implemented by this server",
                    # "href": urljoin(base_url, "conformance"),
                    "href": href_builder.build("conformance"),
                },
                {
                    "rel": Relations.search.value,
                    "type": MimeTypes.geojson,
                    "title": "STAC search",
                    # "href": urljoin(base_url, "search"),
                    "href": href_builder.build("search"),
                    "method": "GET",
                },
                {
                    "rel": Relations.search.value,
                    "type": MimeTypes.geojson,
                    "title": "STAC search",
                    # "href": urljoin(base_url, "search"),
                    "href": href_builder.build("search"),
                    "method": "POST",
                },
            ],
            stac_extensions=extension_schemas,
        )
        return landing_page


@attr.s  # type:ignore
class BaseCoreClient(LandingPageMixin, abc.ABC):
    """Defines a pattern for implementing STAC api core endpoints.

    Attributes:
        extensions: list of registered api extensions.
    """

    base_conformance_classes: List[str] = attr.ib(
        factory=lambda: BASE_CONFORMANCE_CLASSES
    )
    extensions: List[ApiExtension] = attr.ib(default=attr.Factory(list))
    post_request_model = attr.ib(default=BaseSearchPostRequest)

    def conformance_classes(self) -> List[str]:
        """Generate conformance classes by adding extension conformance to base
        conformance classes."""
        base_conformance_classes = self.base_conformance_classes.copy()

        for extension in self.extensions:
            extension_classes = getattr(extension, "conformance_classes", [])
            base_conformance_classes.extend(extension_classes)

        return list(set(base_conformance_classes))

    def extension_is_enabled(self, extension: str) -> bool:
        """Check if an api extension is enabled."""
        return any([type(ext).__name__ == extension for ext in self.extensions])

    def get_extension(self, extension: str) -> ApiExtension:
        extensions = [ext for ext in self.extensions if type(
            ext).__name__ == extension]
        if extensions:
            return extensions[0]
        else:
            raise NotFoundError(f"Extenson {extension} not found")

    def list_conformance_classes(self):
        """Return a list of conformance classes, including implemented extensions."""
        base_conformance = BASE_CONFORMANCE_CLASSES

        for extension in self.extensions:
            extension_classes = getattr(extension, "conformance_classes", [])
            base_conformance.extend(extension_classes)

        return base_conformance

    def landing_page(self, **kwargs) -> stac_types.LandingPage:
        """Landing page.

        Called with `GET /`.

        Returns:
            API landing page, serving as an entry point to the API.
        """
        request: Request = kwargs["request"]
        # base_url = get_base_url(request)
        hrefbuilder = self.href_builder(**kwargs)
        extension_schemas = [
            schema.schema_href for schema in self.extensions if schema.schema_href
        ]
        landing_page = self._landing_page(
            # base_url=base_url,
            href_builder=hrefbuilder,
            conformance_classes=self.conformance_classes(),
            # extension_schemas=[],
            extension_schemas=extension_schemas,
        )

        # Add Queryables link
        if self.extension_is_enabled("FilterExtension"):
            landing_page["links"].append(
                {
                    # TODO: replace this with Relations.queryables.value,
                    "rel": "http://www.opengis.net/def/rel/ogc/1.0/queryables",
                    # TODO: replace this with MimeTypes.jsonschema,
                    "type": "application/schema+json",
                    "title": "Queryables",
                    # "href": urljoin(base_url, "queryables"),
                    "href": hrefbuilder.build("queryables"),
                    "method": "GET",
                }
            )

        # Add Collections links
        collections = self.all_collections(request=kwargs["request"])
        for collection in collections["collections"]:
            landing_page["links"].append(
                {
                    "rel": Relations.child.value,
                    "type": MimeTypes.json.value,
                    "title": collection.get("title") or collection.get("id"),
                    # "href": urljoin(base_url, f"collections/{collection['id']}"),
                    "href": hrefbuilder.build(f"collections/{collection['id']}"),
                }
            )

        # Add OpenAPI URL
        landing_page["links"].append(
            {
                "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0",
                "title": "OpenAPI service description",
                # "href": str(request.url_for("openapi")),
                "href": hrefbuilder.build("api"),
            }
        )

        # Add human readable service-doc
        landing_page["links"].append(
            {
                "rel": "service-doc",
                "type": "text/html",
                "title": "OpenAPI service documentation",
                # "href": str(request.url_for("swagger_ui_html")),
                "href": hrefbuilder.build("api.html"),
            }
        )

        return landing_page

    def conformance(self, **kwargs) -> stac_types.Conformance:
        """Conformance classes.

        Called with `GET /conformance`.

        Returns:
            Conformance classes which the server conforms to.
        """
        return Conformance(conformsTo=self.conformance_classes())
    
    def href_builder(self, **kwargs) -> BaseHrefBuilder:
        """Application href builder.

        Returns:
            BaseHrefBuilder which is used for constructing server hrefs used in responses.
        """
        request: Request = kwargs["request"]
        base_url = str(request.base_url)
        return BaseHrefBuilder(base_url)

    @abc.abstractmethod
    def post_search(
        self, search_request: BaseSearchPostRequest, **kwargs
    ) -> stac_types.ItemCollection:
        """Cross catalog search (POST).

        Called with `POST /search`.

        Args:
            search_request: search request parameters.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    def get_search(
        self,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: Optional[int] = 10,
        query: Optional[str] = None,
        # token: Optional[str] = None,
        pt: Optional[str] = None,
        fields: Optional[List[str]] = None,
        sortby: Optional[str] = None,
        intersects: Optional[str] = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Cross catalog search (GET).

        Called with `GET /search`.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    def get_item(self, item_id: str, collection_id: str, **kwargs) -> stac_types.Item:
        """Get item by id.

        Called with `GET /collections/{collection_id}/items/{item_id}`.

        Args:
            item_id: Id of the item.
            collection_id: Id of the collection.

        Returns:
            Item.
        """
        ...

    @abc.abstractmethod
    def all_collections(self, **kwargs) -> stac_types.Collections:
        """Get all available collections.

        Called with `GET /collections`.

        Returns:
            A list of collections.
        """
        ...

    @abc.abstractmethod
    def get_collection(self, collection_id: str, **kwargs) -> stac_types.Collection:
        """Get collection by id.

        Called with `GET /collections/{collection_id}`.

        Args:
            collection_id: Id of the collection.

        Returns:
            Collection.
        """
        ...

    @abc.abstractmethod
    def item_collection(
        self,
        collection_id: str,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: int = 10,
        # token: str = None,
        pt: str = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Get all items from a specific collection.

        Called with `GET /collections/{collection_id}/items`

        Args:
            collection_id: id of the collection.
            limit: number of items to return.
            #token: pagination token.
            pt: pagination token.

        Returns:
            An ItemCollection.
        """
        ...


@attr.s  # type:ignore
class AsyncBaseCoreClient(LandingPageMixin, abc.ABC):
    """Defines a pattern for implementing STAC api core endpoints.

    Attributes:
        extensions: list of registered api extensions.
    """

    base_conformance_classes: List[str] = attr.ib(
        factory=lambda: BASE_CONFORMANCE_CLASSES
    )
    extensions: List[ApiExtension] = attr.ib(default=attr.Factory(list))
    post_request_model = attr.ib(default=BaseSearchPostRequest)

    def conformance_classes(self) -> List[str]:
        """Generate conformance classes by adding extension conformance to base
        conformance classes."""
        conformance_classes = self.base_conformance_classes.copy()

        for extension in self.extensions:
            extension_classes = getattr(extension, "conformance_classes", [])
            conformance_classes.extend(extension_classes)

        return list(set(conformance_classes))

    def extension_is_enabled(self, extension: str) -> bool:
        """Check if an api extension is enabled."""
        return any([type(ext).__name__ == extension for ext in self.extensions])

    async def landing_page(self, **kwargs) -> stac_types.LandingPage:
        """Landing page.

        Called with `GET /`.

        Returns:
            API landing page, serving as an entry point to the API.
        """
        request: Request = kwargs["request"]
        # base_url = get_base_url(request)
        hrefbuilder = self.href_builder(**kwargs)
        extension_schemas = [
            schema.schema_href for schema in self.extensions if schema.schema_href
        ]
        landing_page = self._landing_page(
            # base_url=base_url,
            href_builder=hrefbuilder,
            conformance_classes=self.conformance_classes(),
            # extension_schemas=[],
            extension_schemas=extension_schemas,
        )

        # Add Queryables link
        if self.extension_is_enabled("FilterExtension"):
            landing_page["links"].append(
                {
                    # TODO: replace this with Relations.queryables.value,
                    "rel": "http://www.opengis.net/def/rel/ogc/1.0/queryables",
                    # TODO: replace this with MimeTypes.jsonschema,
                    "type": "application/schema+json",
                    "title": "Queryables",
                    # "href": urljoin(base_url, "queryables"),
                    "href": hrefbuilder.build("/queryables"),
                    "method": "GET",
                }
            )

        # Add Collections links
        collections = await self.all_collections(request=kwargs["request"])
        for collection in collections["collections"]:
            landing_page["links"].append(
                {
                    "rel": Relations.child.value,
                    "type": MimeTypes.json.value,
                    "title": collection.get("title") or collection.get("id"),
                    # "href": urljoin(base_url, f"collections/{collection['id']}"),
                    "href": hrefbuilder.build(f"collections/{collection['id']}"),
                }
            )

        # Add OpenAPI URL
        landing_page["links"].append(
            {
                "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0",
                "title": "OpenAPI service description",
                # "href": str(request.url_for("openapi")),
                "href": hrefbuilder.build("/api"),
            }
        )

        # Add human readable service-doc
        landing_page["links"].append(
            {
                "rel": "service-doc",
                "type": "text/html",
                "title": "OpenAPI service documentation",
                # "href": str(request.url_for("swagger_ui_html")),
                "href": hrefbuilder.build("/api.html"),
            }
        )

        return landing_page

    async def conformance(self, **kwargs) -> stac_types.Conformance:
        """Conformance classes.

        Called with `GET /conformance`.

        Returns:
            Conformance classes which the server conforms to.
        """
        return Conformance(conformsTo=self.conformance_classes())
    
    async def href_builder(self, **kwargs) -> BaseHrefBuilder:
        """Application href builder.

        Returns:
            BaseHrefBuilder which is used for constructing server hrefs used in responses.
        """
        request: Request = kwargs["request"]
        base_url = str(request.base_url)
        return BaseHrefBuilder(base_url)

    @abc.abstractmethod
    async def post_search(
        self, search_request: BaseSearchPostRequest, **kwargs
    ) -> stac_types.ItemCollection:
        """Cross catalog search (POST).

        Called with `POST /search`.

        Args:
            search_request: search request parameters.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    async def get_search(
        self,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: Optional[int] = 10,
        query: Optional[str] = None,
        # token: Optional[str] = None,
        pt: Optional[str] = None,
        fields: Optional[List[str]] = None,
        sortby: Optional[str] = None,
        intersects: Optional[str] = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Cross catalog search (GET).

        Called with `GET /search`.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    async def get_item(
        self, item_id: str, collection_id: str, **kwargs
    ) -> stac_types.Item:
        """Get item by id.

        Called with `GET /collections/{collection_id}/items/{item_id}`.

        Args:
            item_id: Id of the item.
            collection_id: Id of the collection.

        Returns:
            Item.
        """
        ...

    @abc.abstractmethod
    async def all_collections(self, **kwargs) -> stac_types.Collections:
        """Get all available collections.

        Called with `GET /collections`.

        Returns:
            A list of collections.
        """
        ...

    @abc.abstractmethod
    async def get_collection(
        self, collection_id: str, **kwargs
    ) -> stac_types.Collection:
        """Get collection by id.

        Called with `GET /collections/{collection_id}`.

        Args:
            collection_id: Id of the collection.

        Returns:
            Collection.
        """
        ...

    @abc.abstractmethod
    async def item_collection(
        self,
        collection_id: str,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: int = 10,
        # token: str = None,
        pt: str = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Get all items from a specific collection.

        Called with `GET /collections/{collection_id}/items`

        Args:
            collection_id: id of the collection.
            limit: number of items to return.
            #token: pagination token.
            pt: pagination token.

        Returns:
            An ItemCollection.
        """
        ...


@attr.s
class AsyncBaseFiltersClient(abc.ABC):
    """Defines a pattern for implementing the STAC filter extension."""

    async def get_queryables(
        self, collection_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Get the queryables available for the given collection_id.

        If collection_id is None, returns the intersection of all queryables over all
        collections.

        This base implementation returns a blank queryable schema. This is not allowed
        under OGC CQL but it is allowed by the STAC API Filter Extension
        https://github.com/radiantearth/stac-api-spec/tree/master/fragments/filter#queryables
        """
        return {
            "$schema": "https://json-schema.org/draft/2019-09/schema",
            "$id": "https://example.org/queryables",
            "type": "object",
            "title": "Queryables for Example STAC API",
            "description": "Queryable names for the example STAC API Item Search filter.",
            "properties": {},
        }


@attr.s
class BaseFiltersClient(abc.ABC):
    """Defines a pattern for implementing the STAC filter extension."""

    def get_queryables(
        self, collection_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Get the queryables available for the given collection_id.

        If collection_id is None, returns the intersection of all queryables over all
        collections.

        This base implementation returns a blank queryable schema. This is not allowed
        under OGC CQL but it is allowed by the STAC API Filter Extension
        https://github.com/stac-api-extensions/filter#queryables
        """
        return {
            "$schema": "https://json-schema.org/draft/2019-09/schema",
            "$id": "https://example.org/queryables",
            "type": "object",
            "title": "Queryables for Example STAC API",
            "description": "Queryable names for the example STAC API Item Search filter.",
            "properties": {},
        }
