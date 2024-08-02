"""Api request/response models."""

import importlib.util
from typing import Optional, Type, Union

import attr

# from fastapi import Body, Path
from fastapi import Body, Path, Query
from pydantic import BaseModel, create_model
from pydantic.fields import UndefinedType
from stac_pydantic.shared import BBox

from stac_fastapi.api import descriptions

from stac_fastapi.types.extension import ApiExtension
from stac_fastapi.types.rfc3339 import DateTimeType
from stac_fastapi.types.search import (
    APIRequest,
    BaseSearchGetRequest,
    BaseSearchPostRequest,
    str2bbox,
    str_to_interval,
)


try:
    import orjson  # noqa
    from fastapi.responses import ORJSONResponse as JSONResponse
except ImportError:  # pragma: nocover
    from starlette.responses import JSONResponse


def create_request_model(
    model_name="SearchGetRequest",
    base_model: Union[Type[BaseModel], APIRequest] = BaseSearchGetRequest,
    extensions: Optional[ApiExtension] = None,
    mixins: Optional[Union[BaseModel, APIRequest]] = None,
    request_type: Optional[str] = "GET",
) -> Union[Type[BaseModel], APIRequest]:
    """Create a pydantic model for validating request bodies."""
    fields = {}
    extension_models = []

    # Check extensions for additional parameters to search
    for extension in extensions or []:
        if extension_model := extension.get_request_model(request_type):
            extension_models.append(extension_model)

    mixins = mixins or []

    models = [base_model] + extension_models + mixins

    # Handle GET requests
    if all([issubclass(m, APIRequest) for m in models]):
        return attr.make_class(model_name, attrs={}, bases=tuple(models))

    # Handle POST requests
    elif all([issubclass(m, BaseModel) for m in models]):
        for model in models:
            for k, v in model.__fields__.items():
                field_info = v.field_info
                body = Body(
                    None
                    if isinstance(field_info.default, UndefinedType)
                    else field_info.default,
                    default_factory=field_info.default_factory,
                    alias=field_info.alias,
                    alias_priority=field_info.alias_priority,
                    title=field_info.title,
                    description=field_info.description,
                    const=field_info.const,
                    gt=field_info.gt,
                    ge=field_info.ge,
                    lt=field_info.lt,
                    le=field_info.le,
                    multiple_of=field_info.multiple_of,
                    min_items=field_info.min_items,
                    max_items=field_info.max_items,
                    min_length=field_info.min_length,
                    max_length=field_info.max_length,
                    regex=field_info.regex,
                    extra=field_info.extra,
                )
                fields[k] = (v.outer_type_, body)
        return create_model(model_name, **fields, __base__=base_model)

    raise TypeError("Mixed Request Model types. Check extension request types.")


def create_get_request_model(
    extensions, base_model: BaseSearchGetRequest = BaseSearchGetRequest
):
    """Wrap create_request_model to create the GET request model."""
    return create_request_model(
        "SearchGetRequest",
        base_model=base_model,
        extensions=extensions,
        request_type="GET",
    )


def create_post_request_model(
    extensions, base_model: BaseSearchPostRequest = BaseSearchPostRequest
):
    """Wrap create_request_model to create the POST request model."""
    return create_request_model(
        "SearchPostRequest",
        base_model=base_model,
        extensions=extensions,
        request_type="POST",
    )


@attr.s  # type:ignore
class CollectionUri(APIRequest):
    """Get or delete collection."""

    collection_id: str = attr.ib(
        default=Path(..., description=descriptions.COLLECTION_ID)
    )


@attr.s
class ItemUri(CollectionUri):
    """Get or delete item."""

    item_id: str = attr.ib(default=Path(..., description=descriptions.ITEM_ID))
    crs: Optional[str] = attr.ib(
        default=Query(
            default="http://www.opengis.net/def/crs/OGC/1.3/CRS84",
            description=descriptions.CRS,
        )
    )


@attr.s
class EmptyRequest(APIRequest):
    """Empty request."""

    ...


@attr.s
class ItemCollectionUri(CollectionUri):
    """Get item collection."""

    limit: int = attr.ib(
        default=Query(
            default=10,
            description=descriptions.LIMIT,
        )
    )
    bbox: Optional[BBox] = attr.ib(
        default=Query(
            default=None,
            description=descriptions.BBOX,
        ),
        converter=str2bbox,
    )
    bbox_crs: Optional[str] = attr.ib(
        default=Query(
            default="http://www.opengis.net/def/crs/OGC/1.3/CRS84",
            alias="bbox-crs",
            description=descriptions.BBOX_CRS,
        )
    )
    datetime: Optional[DateTimeType] = attr.ib(
        default=Query(
            default=None,
            description=descriptions.DATETIME,
        ),
        converter=str_to_interval,
    )
    crs: Optional[str] = attr.ib(
        default=Query(
            default="http://www.opengis.net/def/crs/OGC/1.3/CRS84",
            description=descriptions.CRS,
        )
    )
    filter: Optional[str] = attr.ib(default=Query(None, description=descriptions.FILTER))
    filter_lang: Optional[str] = attr.ib(
        default=Query(
            default="cql-json", alias="filter-lang", description=descriptions.FILTER_LANG
        )
    )
    filter_crs: Optional[str] = attr.ib(
        default=Query(
            default="http://www.opengis.net/def/crs/OGC/1.3/CRS84",
            alias="filter-crs",
            description=descriptions.FILTER_CRS,
        )
    )


class POSTTokenPagination(BaseModel):
    """Token pagination model for POST requests."""

    # token: Optional[str] = None
    pt: Optional[str] = None


@attr.s
class GETTokenPagination(APIRequest):
    """Token pagination for GET requests."""

    # token: Optional[str] = attr.ib(default=None)
    pt: Optional[str] = attr.ib(
        default=Query(
            default=None,
            description=descriptions.PAGING_TOKEN,
        )
    )


class POSTPagination(BaseModel):
    """Page based pagination for POST requests."""

    page: Optional[str] = None


@attr.s
class GETPagination(APIRequest):
    """Page based pagination for GET requests."""

    page: Optional[str] = attr.ib(default=None)


class GeoJSONResponse(JSONResponse):
    """JSON with custom, vendor content-type."""

    media_type = "application/geo+json"


class JSONSchemaResponse(JSONResponse):
    """JSON with custom, vendor content-type."""

    media_type = "application/schema+json"
