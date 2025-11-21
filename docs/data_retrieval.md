# Data Retrieval
The data search and retrieval APIs use list-based expressions for filtering results. Each expression begins with an operator, followed by its operands. For instance, the equality test A=B is represented as `["=", A, B]`.

## Operators

Retrieval operators are used to select the locations ("rows") to return.

Attribute operands are represented as objects with an `attribute` key set to either an attribute ID or attribute series ID. When set to an attribute ID (e.g. `USACSSUB->income_1->2025.2`) the exact attribute is used. When set to an attribute series ID (e.g. `USACSSUB->income_1`) the latest available attribute in that series is used.

### Comparison
- `=`, `<>`, `>`, `>=`, `<`, `<=`
    - Standard comparison operators that compare an attribute or the result of an operation with a literal value.
    - Operands: Attribute or operation, string or number.
    - Example: Select all US states.
      ```json
      ["=", {"attribute": "geographicUnit"}, "usa:state"]
      ```
- `startswith`
    - Matches if a text attribute starts with the given string. Matching is case-insensitive and both values may be stripped of diacritics.
    - Operands: A text attribute and string to search for.
    - Example: Search for location names starting with "montreal".
      ```json
      ["startswith", {"attribute": "name"}, "montreal"]
      ```
        - Note that "montreal" matches both "Montreal" and "Montréal".

- `in`, `not in`
    - `in` returns true if the attribute is equal to any of the provided values, `not in` returns true if it is not equal to any.
    - Operands: One attribute followed by one or more strings or numbers.
    - Example: Find three specific ZIP codes by ID.
      ```json
      ["in", {"attribute": "locationSeries"}, "usa:zipCode:90210", "usa:zipCode:10007", "usa:zipCode:33162"]
      ```
        - See [System Attributes](#system-attributes) for details on `locationSeries`.

### Spatial
- `within`
    - Matches locations that are spatially contained in one or more other locations.
    - Operands: one or more location series IDs.
    - Example: locations in either ZIP 90210 or 10007
      ```json
      ["within", "usa:zipCode:90210", "usa:zipCode:10007"]
      ```
- `contains`
    - Matches if the location spatially contains a point given as X, Y coordinates in Web Mercator.
    - Operands: X and Y coordinates in Web Mercator
    - Example: locations that contain the Web Mercator point `-13629430, 4549569`.
      ```json
      ["contains", -13629430, 4549569]
      ```
- `radius`
    - Matches if the location matches the geographic unit and its centroid is within the specified distance of the location whose ID is passed as the last operand, or if it contains the centroid of that location.
    - Operands: geographic unit, radius in meters, location ID
    - Example: return all ZIP codes within 1 km of ZIP code 90210:
      ```json
      ["radius", "usa:zipCode", 1000, "usa:zipCode:90210"]
      ```

### Logic
- `and`
    - Matches if all operands match.
    - Operands: Two or more boolean operations or values.
    - Example: Find USA places starting with "new york".
      ```json
      [
          "and",
          ["startswith", {"attribute": "name"}, "new york"],
          ["=", {"attribute":  "geographicUnit"}, "usa:place"]
      ]
      ```
        - See [System Attributes](#system-attributes) for details on `geographicUnit`.

- `or`
    - Matches if any operands match.
    - Operands: Two or more boolean operations or values.
    - Example: Find ZIP codes with `Median Household Income` above $200,000 or `% Educational Attainment | Bachelor's degree or higher` above 90%.
      ```json
      [
          "and",
          ["=", {"attribute": "geographicUnit"}, "usa:zipCode"],
          [
              "or",
              [">", {"attribute": "USACSSUB->income_1"}, 200000],
              [">", {"attribute": "USACSSUB->education_20_pct"}, 90]
          ]
      ]
      ```
- `not`
    - Inverts its operand: true becomes false and false becomes true.
    - Operands: one boolean operation or value.
    - Example: Select a "donut" of block groups around New York City by selecting block groups within 10 miles, and not those within 5 miles.
      ```json
      [
            "and",
            ["radius", "usa:censusBlockGroup", 16093.44, "usa:place:3651000"],
            ["not", ["radius", "usa:censusBlockGroup", 8046.72, "usa:place:3651000"]]
      ]
      ```

## System Attributes
The following system attributes are available to all users in addition to subscription data.

| Attribute ID                    | Description                                                                                                                                                                             |
|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `locationSeries`                | An ID that uniquely identifies a location regardless of time. This is similar to a "spatial ID" but globally unique. For example, `usa:state:04` always refers to the state of Arizona. |
| `name`                          | The name of a location.                                                                                                                                                                 |
| `geographicUnit`                | The geographic unit of a location. See list below for possible values.                                                                                                                  |
| `censusRelease`                 | The major census release of this location. For US locations this is the decennial census.                                                                                               |
| `geographicRelease`             | The geographic release of a location. This represents updates within a census.                                                                                                          |
| `country`                       | The country of a location.                                                                                                                                                              |
| `extent`                        | The geographic extent (i.e. bounding box) of a location in Web Mercator. The format is `[minX, minY, maxX, maxY]`.                                                                      |
| `polygon`                       | The polygon of a location as a GeoJSON [geometry object](https://www.rfc-editor.org/rfc/rfc7946#section-3.1).                                                                           |
| `polygon->{geographic release}` | Polygon for a specific annual geographic release, e.g. `polygon->2020`. Returned as a GeoJSON [geometry object](https://www.rfc-editor.org/rfc/rfc7946#section-3.1).                    |

Additionally, each location has an attribute for each geographic unit representing parent relationships. For example, a block group has a `usa:censusTract` attribute that indicates its parent census tract. The value is `null` if there is no parent relationship.

Note that some locations have multiple parents of the same unit. For example, it's possible for a ZIP code to be in two places at once. In this case, the parent IDs are returned as pipe (`|`) delimited strings.

### Geographic Units

SimplyAnalytics has data for the following geographic units. Not all datasets have data for all units. The actual units available depend on your data subscription and the units available for your datasets.

### USA:

| Geographic Unit ID           | Name                              |
|------------------------------|-----------------------------------|
| usa                          | USA                               |
| usa:region                   | Regions                           |
| usa:division                 | Divisions                         |
| usa:state                    | States                            |
| usa:dma                      | Nielsen Designated Marketing Area |
| usa:cbsa                     | Core-based Statistical Areas      |
| usa:congressionalDistrict    | Congress. Dist.                   |
| usa:puma                     | PUMAs                             |
| usa:county                   | Counties                          |
| usa:stateUpperDistrict       | State Upper Districts             |
| usa:stateLowerDistrict       | State Lower Districts             |
| usa:secondarySchoolDistrict  | Secondary School Districts        |
| usa:elementarySchoolDistrict | Elementary School Districts       |
| usa:place                    | Cities                            |
| usa:zipCode                  | Zip Codes                         |
| usa:censusTract              | Census Tracts                     |
| usa:censusBlockGroup         | Block Groups                      |
| usa:scrbgh                   | USA Scarborough Crosstab Points   |
| usa:smnncs                   | USA Simmons NCS Crosstab Points   |

#### Canada:

| Geographic Unit ID | Name                     |
|--------------------|--------------------------|
| can                | Canada                   |
| can:province       | Provinces                |
| can:cmaca          | Census Metro Areas       |
| can:cd             | Census Divisions         |
| can:fsa            | Forward Sortation Area   |
| can:csd            | Census Subdivisions      |
| can:ct             | Census Tracts            |
| can:da             | Dissemination Areas      |