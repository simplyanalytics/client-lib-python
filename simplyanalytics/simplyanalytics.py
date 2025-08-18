import requests
from typing import Optional


def attribute(id: str) -> dict:
    return {"attribute": id}


class SimplyAnalyticsClient:
    def __init__(self, key: str, url: Optional[str] = None):
        self.key = key
        self.url = url if url else "https://app.simplyanalytics.com/dispatch.php"
        self._cookies: dict[str, str] = {}

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
        return self.query("get", "attributeDatasetSeries")

    def get_latest_available_datasets(self) -> dict:
        return {
            dataset: details["latestEdition"]
            for dataset, details in self.get_available_datasets().items()
        }

    def get_latest_available_datasets_filter(self) -> list:
        return ["or"] + [
            ["and", ["=", "dataset_series", dataset_series], ["=", "year", edition]]
            for dataset_series, edition in self.get_latest_available_datasets().items()
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

    def get_locations(self, data: dict) -> list:
        return self.query("get", "data/locations2", data)

    def find_attributes(
        self,
        name: str,
        year: Optional[int] = None,
        country: Optional[str] = None,
        census_release: Optional[int] = None,
        limit: int = 100,
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

        return self.get_attributes(
            {
                "where": where,
                "fields": ["attribute", "name", "type"],
                "slice": [0, limit],
                "sort": [["asc", "grouped_order"]],
            }
        )
