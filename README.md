# SA Client Library

A Python library for searching and retrieving SimplyAnalytics data.

## Installation

Download and install with PIP:

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

Store your key either in an environment variable or a `.env` file.