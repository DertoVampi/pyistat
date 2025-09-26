import pandas as pd
import requests
import xml.etree.ElementTree as ET
from .errors import OtherResponseCodeError, WrongFormatError
from .rate_limiter import rate_limiter

all_dataflows = pd.DataFrame() # Cardinal sin: but I used a global variable. It serves ONLY to avoid repeating requests when searching is employed.

@rate_limiter
def get_all_dataflows(returned="dataframe", timeout=30):
    """
    This function is used in the search_dataflows function to search for dataflows,
    but it can also be used alone to get all the possible dataflows.

    Returns
    -------
    df : Returns a pandas DataFrame with all the dataflows if you choose the dataframe.
    csv file: Creates a csv file in the path of your code if you choose the csv.

    """
    # This is the ISTAT url for all dataflows
    global all_dataflows
    if all_dataflows.empty:
        dataflow_url = "https://esploradati.istat.it/SDMXWS/rest/dataflow/ALL/ALL/LATEST"   
        response = requests.get(dataflow_url, timeout=timeout)
        response_code = response.status_code
        if response_code == 200:
            response = response.content.decode('utf-8-sig')
            tree = ET.ElementTree(ET.fromstring(response))
            # Namespaces for ISTAT' SDMX dataflows
            namespaces = {
                'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
                'structure': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
                'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
            }
            data = []
            for dataflow in tree.findall('.//structure:Dataflow', namespaces):
    
                name_it = None
                name_en = None
                for name in dataflow.findall('.//common:Name', namespaces):
                    lang = name.get('{http://www.w3.org/XML/1998/namespace}lang')
                    if lang == 'it':
                        name_it = name.text
                    elif lang == 'en':
                        name_en = name.text
                row = {
                    'id': dataflow.get('id'),
                    'agencyID': dataflow.get('agencyID'),
                    'version': dataflow.get('version'),
                    'isFinal': dataflow.get('isFinal'),
                    'name_it': name_it,
                    'name_en': name_en
                }
                data.append(row)
        else:
            raise OtherResponseCodeError(response_code)
            return None
    else:
        df = all_dataflows
        
    df = pd.DataFrame(data)
    all_dataflows = df # Updates the global variable.
    
    if returned.casefold() == "dataframe" :  
        return df
    elif returned.casefold() == "csv":
        df.to_csv("all_dataflows_ISTAT.csv")
    else:
        raise WrongFormatError()
        
def search_dataflows(search_term, mode="fast", lang="en", returned="dataframe", timeout=30):
    """
    Allows searching for dataflows starting from strings passed. Can also accept a list.

    Parameters
    ----------
    search_term : String or list of strings, 
        is required to perform a search through the datasets.
    mode : String, 
        can be deep or fast. Deep search requires more requests but also gets the dimensions for datasets in a readable way. The default is "fast".
    lang : String, 
        "en" or "it", the language the search will be performed in. The default is "en".
    returned : String, 
        "dataframe" or "csv", the format to be returned. The default is "dataframe".
 
    Raises
    ------
    errors
        OtherResponseCodeError: when the code response from the API URL is not 200.

    Returns
    -------
    df : Returns a pandas DataFrame with all the dataflows if you choose the dataframe.
    csv file: Creates a csv file in the path of your code if you choose the csv.

    """
    global all_dataflows
    if returned != "dataframe" and returned != "csv":
        raise WrongFormatError()
    # The function must accept either single words or lists
    if isinstance(search_term, str):
        search_term = [search_term]
    if all_dataflows.empty:
        df = get_all_dataflows(timeout=timeout)
    else:
        df = all_dataflows
    if df.empty:
        print("Error: cannot retrieve dataflows from the ISTAT API. Open a request on Github.")
        return None
    
    # Initialize dataframe
    search_df = df.copy()
    search_df = search_df.iloc[:0]
    for term in search_term:
        if lang == "en":
            temp_df = df[df["name_en"].str.contains(term, case=False, na=False)]
            search_df = pd.concat([search_df, temp_df], ignore_index=True)
        elif lang == "it":
            temp_df = df[df["name_it"].str.contains(term, case=False, na=False)]
            search_df = pd.concat([search_df, temp_df], ignore_index=True)
        elif lang == "id":
            temp_df = df[df["id"].str.contains(term, case=False, na=False)]
            search_df = pd.concat([search_df, temp_df], ignore_index=True)
        else:
            print("Language not found.")
    if search_df.empty:
        print(f"Warning: the dataflow {term} could not be found. Did you set the right language?")
        return None
    if mode == "fast":
        if returned == "dataframe":
            return search_df
        elif returned == "csv":
            search_df.to_csv("requested_data.csv", index=False)
    if mode =="deep":
        deep_search_df = deep_search(search_df, timeout=timeout)
        if returned == "dataframe":
            return deep_search_df
        elif returned == "csv":
            deep_search_df.to_csv("requested_data.csv", index=False)
        
def format_dimensions(codelist_list): # Format dimensions in a different function to avoid cluttering, only used in deeps_search
    codelist_list = sorted(codelist_list, key=lambda x: x['order'])
    dimension_dict = {}    
    for item in codelist_list:
        dimension_name = item['dimension_name']
        dimension_value = item['dimension_value']
        if dimension_name not in dimension_dict:
            dimension_dict[dimension_name] = []
        if dimension_value not in dimension_dict[dimension_name]:
            dimension_dict[dimension_name].append(dimension_value)

    formatted_parts = [f"{name}={','.join(values)}" for name, values in dimension_dict.items()]
    return ";".join(formatted_parts)

@rate_limiter
def get_dimension_dataflows(dataflow_id, timeout=30):
    """
    This function is called by deep_search and is used to retrieve the data from ISTAT endpoint while tracking the number of requests.

    Parameters
    ----------
    dataflow_id : this is the id, provided by deep_search.

    Raises
    ------
    errors
        OtherResponseCodeError: when the code response from the API URL is not 200.

    Returns
    -------
    tree : the tree that will be parsed by deep_search.

    """
    data_url = f"https://esploradati.istat.it/SDMXWS/rest/availableconstraint/{dataflow_id}/?references=all&detail=full"
    response = requests.get(data_url)
    response_code = response.status_code
    if response_code == 200:
        response = response.content.decode('utf-8-sig')
    else:
        raise OtherResponseCodeError(response_code)
        return None
    tree = ET.ElementTree(ET.fromstring(response))
    return tree
    
def deep_search(df, lang="en", timeout=30):  
    """
    This function is used by the search_dataflows function if the selected mode is "deep".

    Parameters
    ----------
    df : Must be a DataFrame.
    lang : String, 
        used to select the language of the search. The default is "en".

    Raises
    ------
    errors
        OtherResponseCodeError: when the code response from the API URL is not 200.

    Returns
    -------
    df : normal return when used by search_dataflows.

    """
      
    namespaces = {
        'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
        'structure': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
        'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common',
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }
    codelist_list = []
    df["dataflow_dimensions"] = ""
    for index, row in df.iterrows():
        dataflow_id = row["id"]
        tree = get_dimension_dataflows(dataflow_id, timeout=timeout)
        if tree is None:
            print("Error: the dataflow id could not be retrieved. Aborting.")
            return None
        cube_region = tree.find('.//structure:CubeRegion', namespaces)
        key_values = cube_region.findall('.//common:KeyValue', namespaces)

        for codelist in tree.findall(".//structure:Codelist", namespaces):
            codelist_name = codelist.find(f'.//common:Name[@xml:lang="{lang}"]', namespaces).text

            for code in codelist.findall('.//structure:Code', namespaces):
                code_id = code.get('id')

                for idx, key_value in enumerate(key_values):
                    for value in key_value.findall('common:Value', namespaces):
                        if value.text == code_id:
                            codelist_list.append({
                                'dimension_name': codelist_name,
                                'dimension_value': code_id,
                                'order': idx + 1
                            })
                            break
        dict_list = format_dimensions(codelist_list)
        df.at[index, 'dataflow_dimensions'] = dict_list
        
    return df


df = search_dataflows("Coltivazion", lang="it")
