import requests
from typing import Optional


def attribute(id: str) -> dict:
    return {"attribute": id}


class SimplyAnalyticsClient:
    def __init__(self, key: str, url: Optional[str] = None):
        self.key = key
        self.url = url if url else "https://app.simplyanalytics.com/dispatch.php"
        self._cookies: dict[str, str] = {}
        self._institution: dict | None = None
        self._available_datasets: dict | None = None

    def query(self, v: str, r: str, data: Optional[dict] = None):
        params = {"v": v, "r": r}

        if self.key:
            params["k"] = self.key

        response = requests.post(
            self.url, params=params, json=data, cookies=self._cookies
        )

        json = response.json()

        if "exception" in json:
            raise Exception(json["message"])

        return response.json()

    def get_available_datasets(self) -> dict:
        if not self._available_datasets:
            self._available_datasets = self.query("get", "attributeDatasetSeries")
        assert self._available_datasets is not None
        return self._available_datasets

    def get_institution(self) -> dict:
        if not self._institution:
            self._institution = self.query("get", "institution")
        assert self._institution is not None
        return self._institution

    def get_latest_census_releases(self) -> dict[str, int]:
        countries = self.get_institution()["countries"]
        return {
            country: max(int(release) for release in values["censusReleases"].keys())
            for country, values in countries.items()
        }

    def get_latest_census_releases_filter(self) -> list:
        return ["or"] + [
            ["and", ["=", "country", country], ["=", "census_release", release]]
            for country, release in self.get_latest_census_releases().items()
        ]

    def get_latest_available_datasets(self) -> dict:
        return {
            dataset: details["latestEdition"]
            for dataset, details in self.get_available_datasets().items()
        }

    def get_latest_available_datasets_filter(self) -> list:
        return [
            "and",
            ["not", ["=", "h_historical", "true"]],
            ["or"]
            + [
                ["and", ["=", "dataset_series", dataset_series], ["=", "year", edition]]
                for dataset_series, edition in self.get_latest_available_datasets().items()
            ],
        ]

    def get_data_categories(self) -> dict[str, str]:
        return {
            "Popular Data": "popular_data",
            "Population": "population",
            "Age": "age",
            "Gender": "gender",
            "Race & Ethnicity": "race_ethnicity",
            "Income": "income",
            "Education": "education",
            "Jobs & Employment": "jobs_employment",
            "Poverty": "poverty",
            "Language": "language",
            "Ancestry": "ancestry",
            "Immigration": "immigration",
            "Households": "households",
            "Family Type & Marital Status": "family_type",
            "Vehicles & Transportation": "vehicles_transportation",
            "Housing": "housing",
            "Market Segments": "market_segments",
            "Consumer Behavior": "consumer_behavior",
            "Health": "health",
            "Technology": "technology",
            "Finance": "finance",
            "Retail": "retail",
            "Business Counts": "business_counts",
            "Elections": "elections",
            "Other": "other",
        }

    def get_categories_filter(self, categories: list[str]) -> list:
        return [["=", category, "true"] for category in categories]

    def get_any_categories_filter(self, categories: list[str]) -> list:
        return ["or"] + self.get_categories_filter(categories)

    def get_all_categories_filter(self, categories: list[str]) -> list:
        return ["and"] + self.get_categories_filter(categories)

    def get_attributes(self, data: dict) -> list:
        return self.query("get", "attributes", data)["hits"]

    def find_attributes(
        self,
        name: str,
        year: Optional[int] = None,
        country: Optional[str] = None,
        census_release: Optional[int] = None,
        limit: int = 100,
        exact_match: bool = False,
        latest_only: bool = True,
        fields: list[str] = ["attribute", "name", "type"],
    ) -> list:
        where: list[str | int | list] = [
            "and",
            ["=", "status", "visible"],
            ["=" if exact_match else "~", "name", name],
        ]

        if year:
            where.append(["=", "year", year])
        elif latest_only:
            where.append(self.get_latest_available_datasets_filter())

        if country:
            where.append(["=", "country", country])

        if census_release:
            where.append(["=", "censusRelease", census_release])
        else:
            where.append(self.get_latest_census_releases_filter())

        return self.get_attributes(
            {
                "where": where,
                "fields": fields,
                "slice": [0, limit],
                "sort": [["asc", "grouped_order"]],
            }
        )

    def get_locations(self, data: dict) -> list:
        return self.query("get", "data/locations2", data)

    def find_locations(
        self,
        name: str,
        country: Optional[str] = None,
        geographic_unit: Optional[str] = None,
        census_release: Optional[int] = None,
    ) -> list:
        predicates: list = [
            ["startswith", attribute("name"), name],
        ]

        if geographic_unit:
            predicates.append(["=", attribute("geographicUnit"), geographic_unit])
        if census_release:
            predicates.append(["=", attribute("censusRelease"), census_release])
        if country:
            predicates.append(["=", attribute("country"), country])

        where = predicates[0] if len(predicates) == 1 else ["and"] + predicates

        return self.get_locations(
            {
                "select": ["locationSeries", "name", "geographicUnit"],
                "locationSeries": where,
                "sort": [
                    [
                        "desc",
                        "name",
                    ]
                ],
            }
        )

    def get_data(
        self,
        attributes: list[str],
        where: list,
        sort: Optional[list[list]] = None,
        slice: Optional[list[int]] = None,
    ) -> list:
        query = {"select": attributes, "locationSeries": where}

        if sort:
            query["sort"] = sort
        if slice:
            query["slice"] = slice

        return self.get_locations(query)
