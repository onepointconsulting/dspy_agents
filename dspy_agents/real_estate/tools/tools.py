from typing import Optional

import asyncio
import httpx
import json

from bs4 import BeautifulSoup
from dspy_agents.real_estate.model.property import Property
from dspy_agents.logger import logger


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}


def location_search(location: str) -> list[str]:
    return asyncio.run(alocation_search(location))


async def alocation_search(location: str) -> list[str]:
    """Based on some location in the United Kingdom find an location identifier which can be used to get the property search."""
    async with httpx.AsyncClient() as client:
        # Perform an asynchronous GET request
        response = await client.get(
            f"https://livev6-searchapi.savills.com/Suggest/AutoComplete?tenure=GRS_T_B&categoryType=GRS_CAT_RES&term={location}",
            headers=headers,
        )

        # Retrieve the response as a string
        parsed = json.loads(response.text)
        if parsed["Status"] == "OK":
            results = parsed["Results"]
            suggestions = results["Suggestions"]
            id_list = [f'Id_{s["Id"]} Category_{s["Category"]}' for s in suggestions]
            return [json.dumps(id_list)]

        return "Error: could not find property identifier"


property_dict = {
    "apartment": "GRS_PT_APT",
    "new development": "GRS_PT_ND",
    "house": "GRS_PT_H",
}

def property_identifier(property_type: str) -> str:
    return property_dict.get(property_type, "")


def property_search(
    location_identifier: str,
    min_price: Optional[int],
    max_price: int,
    property_types: list[str],
    currency: str = "GBP",
) -> list[str]:
    return asyncio.run(
        aproperty_search(
            location_identifier, min_price, max_price, property_types, currency
        )
    )


async def aproperty_search(
    location_identifier: str,
    min_price: Optional[int],
    max_price: int,
    property_identifiers: list[str],
    currency: str = "GBP",
) -> list[str]:
    """Based on a location, a maximum price and a currency finds multiple real estate properties. The currency is given in a 3 leeter abbreviation, like USD, EUR or GBP"""
    async with httpx.AsyncClient() as client:
        # Perform an asynchronous GET request
        url = f"https://search.savills.com/list?SearchList={location_identifier.replace(" ", "+")}&Tenure=GRS_T_B&SortOrder=SO_PCDD&MaxPrice={max_price}&Currency{currency}&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&SaleableAreaUnit=SquareMeter&Category=GRS_CAT_RES&Shapes=W10"
        if property_identifiers and all([pi in property_dict.values() for pi in property_identifiers]):
            property_types_string = ",".join([str(pt) for pt in property_identifiers])
            url += f"&PropertyTypes={property_types_string}"
        if min_price and min_price > 0:
            url += f"&MinPrice={min_price}"
        print("URL", url)
        response = await client.get(url, headers=headers)

        # Retrieve the response as a string
        soup = BeautifulSoup(response.text)
        main_results = soup.select_one(".sv-results-list__inner")
        items = main_results.select(".sv-results-listing__item")
        properties = []
        for item in items:
            try:
                address1 = item.select_one(".sv-details__address1--truncate")
                address2 = item.select_one(".sv-details__address2")
                size = item.select_one(".sv-property-price__size")
                price = item.select_one(".sv-property-price__wrap")
                features = item.select_one(".sv-list.sv--bullets")
                link = item.select_one(".sv-details__link")
                properties.append(
                    Property(
                        address1=getattr(address1, "text", ""),
                        address2=getattr(address2, "text", ""),
                        size=getattr(size, "text", ""),
                        price=getattr(price, "text", ""),
                        features=getattr(features, "text", ""),
                        link=f"https://search.savills.com{link.get("href", "")}" if link else "",
                    )
                )
            except Exception as e:
                logger.exception(e)
                logger.error("Error occurred")
        return [p.model_dump_json() for p in properties if p.address1 and p.address2]


if __name__ == "__main__":
    from pathlib import Path

    res = asyncio.run(location_search("NW"))
    print(res)
    search_list = json.loads(res)
    res = asyncio.run(property_search(search_list[0], 700000))
    # html = Path("./savills_extract.html")
    # html.write_text(res, encoding="utf-8")
    extract = Path("./savills_extract.json")
    extract.write_text(res, encoding="utf-8")
