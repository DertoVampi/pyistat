# pyistat

# PyIstat: easy ISTAT APIs requests

Documentation for ISTAT APIs is non-existent and this is a shame. After much grief I created a simple module that allows analysts to search and extract data from their APIs without relying on the outdated information that can be found on the Internet.

## How does it work?

PyIstat has two modules: search and get.

### The search module

With the search module, you can easily request all the dataflows together with their structure. If you are looking for all dataflows, simply use get_dataflows().

```from pyistat import search
import pandas as pd

df = get_dataflows()

```
With this code, you'll have a DataFrame with every dataflow available on the ISTAT API. However, if you are looking for a specific dataset, you can use the search_dataflows function.

```
search_term = ["Gross margin", "Energy"]
df = search_dataflows(search_term, mode="fast", lang="en", returned="dataframe")
```

The DataFrame returned will be populated with all the datasets found with those terms in their name. If you want to see what dimensions (keys) and dimension values are available, you can set mode="deep". This will return an additional column with a human-readable set of keys and key values. You can also set the language to lang="it", or you can choose to obtain a .csv file.

```
search_term = ["Gross margin", "Energy"]
search_dataflows(search_term, mode="deep", lang="it", returned="csv"
```

### The get module

After finding the datasets you are most interested in, it's time to get that data from ISTAT APIs. First of all, you can check the dimensions and their ordering by using get_dimensions.

```
dimensions_df = get_dimensions(dataflow_id)
```

This will return all the dimensions and their meaning in a readable DataFrame (use Spyder or another IDE with a variable explorer to make it even easier to read). The order of the dimensions will also be displayed, in case you want to pass a list with the dimensions. If you do not want to pass a list, you can pass dimensions as arguments of the function.

```
# Either pass a list with the ordered dimensions...
dimensions = ["Q", "W", "", "", "", ""] # Make sure to leave the unwanted dimensions with "".
pil_df = get_data("163_156_DF_DCCN_SQCQ_3", dimensions, start_period=2020)


# Or use kwargs...
pil_df = get_data("163_156_DF_DCCN_SQCQ_3", end_period=2024, updated_after=2023, freq="Q", correz="W", returned="csv")

# Or simply get the full data available.
pil_df = get_data("163_156_DF_DCCN_SQCQ_3")
```

There is an additional variable you can pass to the get_data function, which is force_url=True. Normally, the function checks whether the number of dimensions assigned is the same as the dimensions the dataflow requires, and whether the dimension values you provide are consistent with those of the dataflow. However, for unknown reasons, sometimes the number of dimension found in the structure XML is different from what the dataflow actually requires... In this case, if you are confident the URL is correct (maybe try it in the browser first), you can pass force_url=True to skip the controls.

### To do

I made this module as I found the lack of documentation from ISTAT regarding their API access incredibly frustrating. I needed a quick way to get the data from their APIs in order to improve my data pipeline. However, this code needs some refining still; as of now, it works, but it can be more efficient.

If it gains traction I'd be more than happy to fix it wherever there is the need of fixing.

To do: a .exe that is system-and language-agnostic.
Fix inefficiencies in the code.
