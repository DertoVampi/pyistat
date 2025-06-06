# PyIstat: easy ISTAT APIs requests

Easy ISTAT APIs to get data from ISTAT datasets, written in Python.

Documentation for ISTAT APIs is almost non-existent, what exists is often outdated, and this is a shame. After much grief I created a simple module that allows analysts to search and extract data from their APIs without relying on the outdated information that can be found on the Internet.

In practice, pyistat abstracts the API calls to ISTAT and requires no previous knowledge of XMLs and requests. It is perfect for automating data extraction from fresh datasets and is optimized to require 0 maintenance after setup.

This module also offers users accurate checks to see if the requests is valid or not, and does not require you to always check the validity of a request on your browser. It also allows the usage of start and end periods, and updatedAfter keys.

I hope this is what you are looking for! Enjoy querying ISTAT APIs to your heart's content. Happy data analysis!

## How does it work?

PyIstat has two modules: search and get. To use it in Python simply install it via pip. They are built to work with pandas, so make sure to import pandas to make full use of the modules. Technically you can also download every query as a .csv but it gets clunky over time.

```
pip install pyistat
import pandas as pd
```
### The search module

With the search module, you can easily request all the ISTAT dataflows together with their structure. If you are looking for all dataflows, simply use get_dataflows().

```
from pyistat import search
import pandas as pd

df = search.get_dataflows()

```
With this code, you'll have a DataFrame with every dataflow available on the ISTAT API. However, if you are looking for a specific dataset, you can use the search_dataflows function.

```
search_term = ["Gross margin", "Energy"]
df = search.search_dataflows(search_term, mode="fast", lang="en", returned="dataframe")
```

The DataFrame returned will be populated with all the datasets found with those terms in their name. If you want to see what dimensions (keys) and dimension values are available, you can set mode="deep". This will return an additional column with a human-readable set of keys and key values. You can also set the language to lang="it", or you can choose to obtain a .csv file.

```
search_term = ["Gross margin", "Energy"]
search.search_dataflows(search_term, mode="deep", lang="it", returned="csv"
```

### The get module

After finding the datasets you are most interested in, it's time to get that data from ISTAT APIs. First of all, you can check the dimensions and their ordering by using get_dimensions.

```
from pyistat import get

dimensions_df = get.get_dimensions(dataflow_id)
```

This will return all the dimensions and their meaning in a readable DataFrame (use Spyder or another IDE with a variable explorer to make it even easier to read). The order of the dimensions will also be displayed, in case you want to pass a list with the dimensions. If you do not want to pass a list, you can pass dimensions as arguments of the function.

```
# Either pass a list with the ordered dimensions...
dimensions = ["Q", "W", "", "", "", ""] # Make sure to leave the unwanted dimensions with "".
pil_df = get.get_data("163_156_DF_DCCN_SQCQ_3", dimensions, start_period=2020)


# Or use kwargs...
pil_df = get.get_data("163_156_DF_DCCN_SQCQ_3", end_period=2023, updated_after=2023, freq="Q", correz="W", returned="csv")

# Or simply get the full data available.
pil_df = get.get_data("163_156_DF_DCCN_SQCQ_3")
```
Finally, take care of the select_last_edition variable set to True by default: it allows you to always fetch fresh data from the Istat APIs. Make sure to use it if you want an hassle-free code. If you prefer manually assigning your editions, set select_last_edition=False in get_data.
```
pil_df = get.get_data("163_156_DF_DCCN_SQCQ_3", t_bis="2025M3", select_last_edition=False)

```
There is an additional variable you can pass to the get_data function, which is force_url=True. Normally, the function checks whether the number of dimensions assigned is the same as the dimensions the dataflow requires, and whether the dimension values you provide are consistent with those of the dataflow. However, for unknown reasons, sometimes the number of dimension found in the structure XML is different from what the dataflow actually requires... In this case, if you are confident the URL is correct (maybe try it in the browser first), you can pass force_url=True to skip the controls.

### To do

I made this module as I found the lack of documentation from ISTAT regarding their API access incredibly frustrating. I needed a quick way to get the data from their APIs in order to improve my data pipeline. However, this code needs some refining still; as of now, it works, but it can be more efficient.

If it gains traction I'd be more than happy to fix it wherever there is the need.

To do: Fix inefficiencies in the code. Comment the code more. Add a graphic way to setup queries.

Last fixes: Changed the logic with which the search module searched for dimensions and constraints, making it consistent with what you get from get.get_dimensions. Improved efficiency of the code. Added commenting. Added select_last_edition functionality. Minor bugfixes.