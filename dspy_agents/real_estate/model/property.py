from typing import Optional
from pydantic import BaseModel, Field


class Property(BaseModel):
    address1: str = Field(
        ...,
        description="The first address of the property",
        examples="St. John's Wood High Street",
    )
    address2: Optional[str] = Field(
        ...,
        description="The first address of the property",
        examples="St. John's Wood High Street",
    )
    size: str = Field(..., description="The size of the property")
    price: Optional[str] = Field(..., description="The size of the property")
    features: Optional[str] = Field(..., description="The features of the property")
    link: Optional[str] = Field(..., description="The size of the property")


class PropertyList(BaseModel):
    properties: list[Property] = Field(
        ..., description="The list of real estate properties"
    )
