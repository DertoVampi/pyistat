# PyIstat: easy ISTAT APIs requests

Easy ISTAT APIs to get data from ISTAT datasets, written in Python.

Codeberg is cool: https://codeberg.org/Derto/pyistat

Documentation for ISTAT APIs is non-existent, what little exists is often outdated, and this is a shame. After much grief I created a simple module that allows analysts to search and extract data from their APIs without relying on the outdated information that can be found on the Internet. The module also handles the requests limit.

In practice, pyistat abstracts the API calls to ISTAT and requires no previous knowledge of XMLs and requests. It is perfect for automating data extraction from fresh datasets and is optimized to require 0 maintenance after setup.

This module also offers users accurate checks to see if the requests is valid or not, and does not require you to always check the validity of a request on your browser. It also allows the usage of start and end periods, and updatedAfter keys.

I am an avid Spyder user, and its Variable Explorer is truly a blessing when working with data. I suggest you download it and use its Variable Explorer to substitute CSV and Excels for data work with a limited amount of information! You can download their installer here: https://www.spyder-ide.org/

I hope this is what you are looking for! Enjoy querying ISTAT APIs to your heart's content. Happy data analysis!

## Important Update

1.2.x UPDATE: After the new update, pandas is no longer a dependency. Now results are fetched as a list of dictionaries, fully compatible with pandas and polars. Make sure to UPDATE YOUR CODE or PYISTAT won't work if you update the library!

UPDATE: The new limitations imposed by ISTAT are the following: 5 requests/minute or the IP will be banned for 1 to 2 days. I updated the code to track the requests and pause them until it is safe to resume. It is advised not to re-run the code from multiple kernels and to stick with one computer at a time running it. The thread lock is implemented in the wrapper function but I can't swear by it... It needs testing!


---


## How does it work?

PyIstat has two modules: search and get. To use it in Python simply install it via pip. They are built to work with pandas or polars, so make sure to import pandas to make full use of the modules. Technically you can also download every query as a .csv but it gets clunky over time.

```
pip install pyistat
import pandas as pd
# or...
import polars as pl
```

### The search module

With the search module, you can easily request all the ISTAT dataflows together with their structure. If you are looking for all dataflows, simply use get_dataflows().

```
from pyistat import search
import pandas as pd

list = search.get_dataflows()
df = pd.DataFrame(list)

```
With this code, you'll have a DataFrame with every dataflow available on the ISTAT API. However, if you are looking for a specific dataset, you can use the search_dataflows function.

```
search_term = ["Gross margin", "Energy"]
list = search.search_dataflows(search_term, mode="fast", lang="en", returned="list")
df = pl.DataFrame(list)
```

The list of dictionaries returned will be populated with all the datasets found with those terms in their name. If you want to see what dimensions (keys) and dimension values are available, you can set mode="deep". This will return an additional column with a human-readable set of keys and key values. You can also set the language to lang="it", or you can choose to obtain a .csv file., which will be saved by default in your code directory.

```
search_term = ["Gross margin", "Energy"]
search.search_dataflows(search_term, mode="deep", lang="it", returned="csv", csv_name = "search_result.csv")
```

Pay attention to missing mappings: some dataflows such as 151_914_DF_DCCV_TAXDISOCCU1_YOUTH are bugged on ISTAT's side (tested 7th March, 2026) as they miss the mappings. They will not raise an error but will print the response code to the terminal.

### The get module

After finding the datasets you are most interested in, it's time to get that data from ISTAT APIs. First of all, you can check the dimensions and their ordering by using get_dimensions.

```
from pyistat import get

dimensions_list = get.get_dimensions(dataflow_id)
```

This will return all the dimensions and their meaning in a list of dictionaries (use Spyder or another IDE with a variable explorer to make it even easier to read after you transform it into a DataFrame). The order of the dimensions will also be displayed, in case you want to pass a list with the dimensions. If you do not want to pass a list, you can pass dimensions as key arguments (kwargs) of the function.

```
# Either pass a list with the ordered dimensions...
dimensions = ["Q", "W", "", "", "", ""] # Make sure to place a "" for dimensions you do not want to filter!
pil_list = get.get_data("163_156_DF_DCCN_SQCQ_3", dimensions, start_period=2020, test_rows=5)


# Or use kwargs...
pil_list = get.get_data("163_156_DF_DCCN_SQCQ_3", end_period=2023, updated_after=2023, freq="Q", correz="W", returned="csv", test_rows=-5)

# Or simply get the full data available. Try not to, though! Datasets can be very large and they can overload ISTAT's servers.
pil_list = get.get_data("163_156_DF_DCCN_SQCQ_3", timeout=120)
```

You see here you can pass a test_rows value. When testing queries, make sure to set a test_rows cap as it will sensibly decrease query time and you will not weigh too much on the servers. After the query is final, you can safely remove it.

Another variable is timeout: apply it to a function that requests a large dataset to ensure its dispatch. Standard value is 60 seconds.

Finally, take care of the select_last_edition variable set to True by default: it allows you to always fetch fresh data from the Istat APIs. Make sure to use it if you want an hassle-free code. If you prefer to manually assign your editions, set select_last_edition=False in get_data. You can also use the t_bis variable without setting select_last_edition to False, but there is a nag for it.

```
pil_list = get.get_data("163_156_DF_DCCN_SQCQ_3", t_bis="2025M3", select_last_edition=False)
```


UPDATE 1.2: the following bug should be patched. Please tell me if some error arises.


_There is an additional variable you can pass to the get_data function, which is force_url=True. Normally, the function checks whether the number of dimensions assigned is the same as the dimensions the dataflow requires, and whether the dimension values you provide are consistent with those of the dataflow. However, for unknown reasons, sometimes the number of dimension found in the structure XML is different from what the dataflow actually requires... In this case, if you are confident the URL is correct (maybe try it in the browser first), you can pass force_url=True to skip the controls._




### To do

I made this module as I found the lack of documentation from ISTAT regarding their API access incredibly frustrating. I needed a quick way to get the data from their APIs in order to improve my data pipeline. However, this code needs some refining still; as of now, it works, but it can be more efficient.

If it gains traction I'd be more than happy to fix it wherever there is the need.

To do: Add a graphic way to setup queries. Implement Classes instead of Functions.


---


Last fixes: 

1.2.2: 
- Added basic logging support instead of prints.

1.2.1: 
- You will find this version on PyPi! But there are no differences. Refer to the 1.2.0 patch notes.

1.2.0:
- Removed the pandas dependency, now you can use pyistat without installing it and you can also use it with polars or anything else hassle-free. 
- Added the variable "test_rows" to make it easier and clearer to test queries without using the start_date variable. You're welcome, servers.
- Added an error that will ping the user when they try to return a DataFrame.
- Fixed a critical bug that sometimes broke the wrapper leading to ISTAT blocking the IP.
- Minor code quality improvements.
- Switched to uv to package and publish.

1.1.2:
- Added the timeout variable, useful when requesting large datasets.

1.1.1:
- Changed the pyproject.toml dependencies.

1.1.0:
- After the new ISTAT restrictions I released new code to count and track requests and avoid them with a decorator function that prevents requesting more than 5 calls/minute. It pauses the code and it then is resumed after 60 seconds.

1.0.4: 
- After ISTAT put unreasonable restrictions on data requests, I have been forced to use global variables to avoid as many requests as possible. Need testing to see if it is enough.

1.0.3: 
- Fixed a bug that occurred when kwargs were used together with force_url. Now, force_url has no effect when kwargs are used, as the positioning of values must be extracted from the dimension_df. 
- Added a debug_url set to False to get.get_data. Setting it to True prints the generated url for manual debugging. 

1.0.2: Changed the logic with which the search module searched for dimensions and constraints, making it consistent with what you get from get.get_dimensions. Improved efficiency of the code. Added commenting. Added select_last_edition functionality. Minor bugfixes.
