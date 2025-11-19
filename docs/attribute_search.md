# Attribute Search
The data search and retrieval APIs use list-based expressions for filtering results. Each expression begins with an operator, followed by its operands. For instance, the equality test A=B is represented as `["=", A, B]`.

## Operators

Search operators are used to explore and find SimplyAnalytics attributes (or "variables".)

See [Attribute Metadata](#attribute-metadata) for possible fields to search.

### Comparison
- `=`
    - Matches a field exactly.
    - Example: Find all attributes where the name is exactly `# Total Population`:
      ```json
      ["=", "name", "# Total Population"]
      ```
- `<`, `>`
    - Matches less than/greater than.
    - Example: Find income range attributes up to $100,000:
      ```json
      ["<", "income_min", 100000]
      ```
- `~`
    - Fuzzy matches a string.
    - Example: Find attributes where name contains "population":
      ```json
      ["~", "name", "population"]
      ```
- `startswith`
    - Matches fields starting with the given value.
    - Example: Find attributes where name starts with "# Total":
      ```json
      ["startswith", "name", "# Total"]
      ```  
- `in`
    - Matches where field is one of several exact values.
    - Example: Find attributes from years 2010 and 2020:
      ```json
      ["in", "year", [2010, 2020]]
      ```

### Logic
- `and`, `or`
    - Matches if all or any arguments match respectively.
    - Example: Find "population" attributes from 2010 and 2020:
      ```json
      ["and", ["in", "year", [2010, 2020]], ["~", "name", "population"]]
      ```
- `not`
    - Inverts another operator.
    - Example: Skip data tagged as historical:
    ```json
    ["not", ["=", "h_historical", "true"]]
    ```

## Attribute Metadata

SimplyAnalytics provides metadata fields for attributes. These can be accessed through the attribute search API.

| Field               | Description                                                                                                                                                                                                                                                                |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| attribute           | A unique attribute ID. For example, `USACSSUB->population_1->2026.1` is a permanent and unique ID for a 2026 `# Total Population` attribute.                                                                                                                               |
| attribute_series    | A unique attribute series ID. Attributes in the same series differ only by year and can be compared over time. For example, `USACSSUB->population_1` is the attribute series ID for all `# Total Population` attributes.                                                   |
| name                | The attribute name.                                                                                                                                                                                                                                                        |
| type                | The attribute type. See [list](#attribute-types) below for possible values.                                                                                                                                                                                                |
| definition          | A text description of the attribute definition, if available.                                                                                                                                                                                                              |
| source              | The attribute source agency.                                                                                                                                                                                                                                               |
| year                | The year and edition of the attribute.                                                                                                                                                                                                                                     |
| census_release      | The census release year (e.g. 2010, 2020).                                                                                                                                                                                                                                 |
| geographic_release  | The geographic release year within a census release. This is not necessarily the same as the attribute year. For example, it's possible to have a 2025 attribute in 2022 geographies.                                                                                      |
| dataset_id          | A unique ID of the dataset this attribute is from. For example, dataset ID `USACSSUB->2026.1` is the 2026 edition of `SimplyAnalytics & US Census Bureau American Community Survey Data`.                                                                                  |
| dataset_series      | The unique dataset series ID this attribute belongs to. Datasets in the same series differ only by year and can be compared over time. For example, dataset series `USACSSUB` contains all `SimplyAnalytics & US Census Bureau American Community Survey Data` attributes. |
| dataset_series_name | The name of the dataset series.                                                                                                                                                                                                                                            |
| vendor              | The name of the data vendor.                                                                                                                                                                                                                                               |
| country             | The attribute country.                                                                                                                                                                                                                                                     |
| income_min          | The minimum income for income range attributes.                                                                                                                                                                                                                            |
| income_max          | The maximum income for income range attributes.                                                                                                                                                                                                                            |
| age_min             | The minimum age for age range attributes.                                                                                                                                                                                                                                  |
| age_max             | The maximum age for age range attributes.                                                                                                                                                                                                                                  |

## Attribute Types

SimplyAnalytics provides the following attribute types:

| Type    | Example                               |
|---------|---------------------------------------|
| count   | `# Total Population`                  |
| percent | `% Household Income $100,000 or more` |
| mean    | `Average Household Income`            |
| median  | `Housing Median Value`                |

