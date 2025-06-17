import requests
from typing import Optional


def attribute(id: str) -> dict:
    return {"attribute": id}


class SimplyAnalyticsClient:
    def __init__(self, key: str, url: Optional[str] = None):
        self.key = key
        self.url = url if url else "https://app.simplyanalytics.com/dispatch.php"
        self._cookies: dict[str, str] = {}

    def query(self, v: str, r: str, data: dict):
        params = {"v": v, "r": r}

        if self.key:
            params["k"] = self.key

        response = requests.post(
            self.url,
            params=params,
            json=data,
            cookies=self._cookies
        )

        json = response.json()

        if 'exception' in json:
            raise Exception(json['message'])

        return response.json()

    def get_attributes(self, data: dict) -> list:
        return self.query("get", "attributes", data)['hits']

    def get_locations(self, data: dict) -> list:
        return self.query("get", "data/locations2", data)

    def find_attributes(
        self,
        name: str,
        year: Optional[int] = None,
        country: Optional[str] = None,
        census_release: Optional[int] = None,
        limit: int = 100
    ) -> list:
        where: list[str | int | list] = [
            "and",
            ["=", "status", "visible"],
            ["~", "name", name],
        ]

        if year:
            where.append(["=", "year", year])
        if country:
            where.append(["=", "country", country])
        if census_release:
            where.append(["=", "censusRelease", census_release])

        return self.get_attributes({
            "where": where,
            "fields": ["attribute", "name", "type"],
            "slice": [0, limit],
            "sort": [["asc", "grouped_order"]]
        })
