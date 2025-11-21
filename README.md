# SimplyAnalytics Client Library

Python library for searching and retrieving SimplyAnalytics data.

## Installation

Install using pip:

```shell
pip install git+https://github.com/simplyanalytics/client-lib-python
```

## Usage

Create a client with your SimplyAnalytics API key. Using `dotenv`:

```python
from simplyanalytics import SimplyAnalyticsClient
from dotenv import load_dotenv
import os


load_dotenv()

client = SimplyAnalyticsClient(os.getenv('SA_KEY'))
```

**Note:** Store your key either in an environment variable or a `.env` file.

## Finding and Retrieving Data

SimplyAnalytics represents data as _attributes_ of _locations_. Attributes and locations are further organized into time series.

To access data, you'll need:
- IDs of the attributes you want to retrieve
- A filter to select specific locations

You can find attribute IDs using the SimplyAnalytics application or the provided Python functions.

Both APIs use list-based expressions for filtering results. See [docs/attribute_search.md](docs/attribute_search.md) and [docs/data_retrieval.md](docs/data_retrieval.md) for more information.

## Examples

### Find Attributes

Find the most recent available attributes related to total population:

```python
print(client.find_attributes("total population"))
```
```json
[["USACSSUB->population_1->2025.2", "# Total Population", "count"], ["USACSSUB->population_2->2025.2", "# Sex | Total population", "count"],  ...
```
**Note:** Each result contains the attribute ID, name and type. Use the `fields` parameter to request other fields.

### Find Locations

Find all places (cities, towns, etc.) with "new york" in name:

```python
print(client.find_locations("new york", geographic_unit="usa:place"))
```
```json
[["usa:place:3651000", "New York, NY", "usa:place"], ["usa:place:3651011", "New York Mills, NY", "usa:place"], ["usa:place:2746060", "New York Mills, MN", "usa:place"]]
```
**Notes:**
- Each result includes a location series ID for data selection, plus the location name and geographic unit.
- `geographic_unit` is optional. [View available geographic units](docs/data_retrieval.md#geographic-units).

### Get Attribute Data for a Specific Location

Get the 2025 total population for Seattle, WA by matching on the location name:

```python
from simplyanalytics import attribute

results = client.get_data(
    ["USACSSUB->population_1->2025.2"],
    ["=", attribute("name"), "Seattle, WA"]
)
print(results)
```
```json
[[739028]]
```
**Notes:**
- Attributes referenced in a filter or sort are represented as JSON objects or Python dictionaries in the form `{"attribute": id}`.
- Use the `attribute()` function to create a dictionary for a given ID.
- `name`  is a system attribute provided by SimplyAnalytics.
- See [System Attributes](docs/data_retrieval.md#system-attributes) for available options.

### Get Attribute Data for All Locations of a Geographic Unit

Get the 2025 total population and names for all USA states, in descending order:

```python
from simplyanalytics import attribute

results = client.get_data(
    ["USACSSUB->population_1->2025.2", "name"],
    ["=", attribute("geographicUnit"), "usa:state"],
    sort=[("desc", attribute("USACSSUB->population_1->2025.2"))],
)
print(results)
```
```json
[[39206929, "California"], [30284032, "Texas"], [22380747, "Florida"], [20207288, "New York"], [13143025, "Pennsylvania"], ...
```
**Notes:**
- `geographicUnit` is a system attribute provided by SimplyAnalytics.
- See [System Attributes](docs/data_retrieval.md#system-attributes) for available options.

### Get Attribute Data for ZIP Codes in a City

Get the top 10 most populous ZIP codes in New York, NY, by latest estimate:

```python
from simplyanalytics import attribute

results = client.get_data(
    ["USACSSUB->population_1", "name"],
    [
        "and",
        ["=", attribute("usa:place"), "usa:place:3651000"],
        ["=", attribute("geographicUnit"), "usa:zipCode"],
    ],
    sort=[("desc", attribute("USACSSUB->population_1"))],
    slice=(0, 10),
)
```
```json
[[894740, "10468, Bronx, NY"], [866016, "11368, Corona, NY"], [791728, "11219, Brooklyn, NY"], [697023, "11223, Brooklyn, NY"], [696078, "11375, Forest Hills, NY"], [681896, "11204, Brooklyn, NY"], [679672, "11207, Brooklyn, NY"], [654556, "10467, Bronx, NY"], [648621, "11215, Brooklyn, NY"], [633330, "10460, Bronx, NY"]]
```
**Notes**:
- The `usa:place` attribute contains the place the location is in, if any. `usa:place:3651000` is the ID of "New York, NY" as seen in the [Find Locations example](#find-locations).
- `slice` is used to return a subset of results.

### Get Attribute Data for Block Groups in a Radius

Get data for ZIP codes within a 1000-meter radius of ZIP code 90210:

```python
results = client.get_data(
    ["USACSSUB->population_1", "name"],
    ["radius", "usa:zipCode", 1000, "usa:zipCode:90210"]
)
print(results)
```
```json
[[20394, "90069, West Hollywood, CA"], [19710, "90210, Beverly Hills, CA"], [8768, "90211, Beverly Hills, CA"], [10010, "90212, Beverly Hills, CA"]]
```
**Notes:**
- The ZIP code itself is included.
- The "radius" is an irregular shaped buffer around the target location. See [Spatial Operators](docs/data_retrieval.md#spatial) for implementation details.

### Aggregate Attribute Data of Block Groups in a Radius

Aggregate block group data for `# Total Population` and `% Sex | Male`:

```python
results = client.aggregate_data(
    ["USACSSUB->population_1", "USACSSUB->population_3_pct"],
    ["radius", "usa:censusBlockGroup", 1000, "usa:zipCode:90210"]
)
print(results)
```
```json
[[58882, 51.7934]]
```
**Notes:**
- `USACSSUB->population_3_pct` is `% Sex | Male` and the returned aggregate is the total sum of `# Sex | Male` divided by the total sum of `# Sex | Total population` of the selected block groups.
- For attributes which cannot be aggregated, such as some medians and percents, `null` is returned.