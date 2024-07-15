"""Request model for the Crs extension."""

#from typing import Optional
from typing import Literal, Optional

import attr
#from pydantic import BaseModel
from pydantic import BaseModel, Field

from stac_fastapi.types.search import APIRequest

# What URL CRS that is allowed
crs_url = Literal["http://www.opengis.net/def/crs/OGC/1.3/CRS84", "http://www.opengis.net/def/crs/EPSG/0/25832"]

@attr.s
class CrsExtensionGetRequest(APIRequest):
    """Crs Extension GET request model."""

    crs: Optional[crs_url] = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
    bbox_crs: Optional[crs_url]  = Field(default="http://www.opengis.net/def/crs/OGC/1.3/CRS84", alias="bbox-crs")


class CrsExtensionPostRequest(BaseModel):
    """Crs Extension POST request model."""

    crs: Optional[crs_url] = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
    bbox_crs: Optional[crs_url]  = Field(default="http://www.opengis.net/def/crs/OGC/1.3/CRS84", alias="bbox-crs")
