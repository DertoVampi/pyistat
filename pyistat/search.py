import csv
import requests
import xml.etree.ElementTree as ET
from .errors import OtherResponseCodeError, WrongFormatError, MappingsError
from .rate_limiter import rate_limiter

all_dataflows = []  # Cardinal sin: but I used a global variable. It serves ONLY to avoid repeating requests when searching is employed.

def write_to_csv(data, csv_name):
    with open(csv_name, mode="w", newline="") as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

@rate_limiter
def get_all_dataflows(returned="", timeout=30, csv_name="all_dataflows_ISTAT.csv"):
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
    if not all_dataflows:
        dataflow_url = (
            "https://esploradati.istat.it/SDMXWS/rest/dataflow/ALL/ALL/LATEST"
        )
        response = requests.get(dataflow_url, timeout=timeout)
        response_code = response.status_code
        if response_code == 200:
            response = response.content.decode("utf-8-sig")
            tree = ET.ElementTree(ET.fromstring(response))
            # Namespaces for ISTAT' SDMX dataflows
            namespaces = {
                "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
                "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
                "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
            }
            data = []
            for dataflow in tree.findall(".//structure:Dataflow", namespaces):

                name_it = None
                name_en = None
                for name in dataflow.findall(".//common:Name", namespaces):
                    lang = name.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang == "it":
                        name_it = name.text
                    elif lang == "en":
                        name_en = name.text
                row = {
                    "id": dataflow.get("id"),
                    "agencyID": dataflow.get("agencyID"),
                    "version": dataflow.get("version"),
                    "isFinal": dataflow.get("isFinal"),
                    "name_it": name_it,
                    "name_en": name_en,
                }
                data.append(row)
        else:
            raise OtherResponseCodeError(response_code)
            return None
    else:
        data = all_dataflows

    ###
    all_dataflows = data  # This updates the global variable. Don't forget!!!
    ###
    
    if returned.casefold() == "":
        return data
    elif returned.casefold() == "csv":
        write_to_csv(data, csv_name)
    else:
        raise WrongFormatError()


def search_dataflows(
    search_term, mode="fast", lang="en", returned="", timeout=30, csv_name=""
):
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
    if returned != "" and returned != "csv":
        raise WrongFormatError()
    # The function must accept either single words or lists
    if isinstance(search_term, str):
        search_term = [search_term]
    if not all_dataflows:
        data = get_all_dataflows(timeout=timeout)
    else:
        data = all_dataflows
    if not data or data == "":
        print(
            "Error: cannot retrieve dataflows from the ISTAT API. Open a request on Github."
        )
        return None

    # Initialize dataframe
    search_result = []
    for term in search_term:
        lang = lang.casefold()
        if lang not in ("it", "en", "id"):
            print("Language not found. Available: en, it, id.")
        for row in data:
            if lang.casefold() == "en" and row["name_en"]:
                if term.casefold() in row["name_en"].casefold():
                    search_result.append(row)
            elif lang.casefold() == "it" and row["name_it"]:
                if term.casefold() in row["name_it"].casefold():
                    search_result.append(row)
            elif lang.casefold() == "id" and row["id"]:
                if term.casefold() in row["id"].casefold():
                    search_result.append(row)
            else:
                print(f"Warning: there is no name assigned to the following dataflow id: {row['id']}.")

    if not search_result:
        print(
            f"Warning: the dataflow {term} could not be found. Did you set the right language?"
        )
        return None
    if mode == "fast":
        if returned == "":
            return search_result
        elif returned == "csv":
            if csv_name == "":
                csv_name = f"{search_term}.csv"
            write_to_csv(search_result, csv_name)
    if mode == "deep":
        deep_search_result = deep_search(search_result, timeout=timeout)
        if returned == "":
            return deep_search_result
        elif returned == "csv":
            if csv_name == "":
                csv_name = f"{search_term}.csv"
            write_to_csv(deep_search_result, csv_name)


def format_dimensions(
    codelist_list,
):  # Format dimensions in a different function to avoid cluttering, only used in deeps_search
    codelist_list = sorted(codelist_list, key=lambda x: x["order"])
    dimension_dict = {}
    for item in codelist_list:
        dimension_name = item["dimension_name"]
        dimension_value = item["dimension_value"]
        if dimension_name not in dimension_dict:
            dimension_dict[dimension_name] = []
        if dimension_value not in dimension_dict[dimension_name]:
            dimension_dict[dimension_name].append(dimension_value)

    formatted_parts = [
        f"{name}={','.join(values)}" for name, values in dimension_dict.items()
    ]
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
    response_text = response.text
    if response_code == 200:
        response = response.content.decode("utf-8-sig")
    elif response_code == 500:
        raise MappingsError(dataflow_id, response_code, response_text)
    else:
        raise OtherResponseCodeError(response_code, response_text)
        # return None
    tree = ET.ElementTree(ET.fromstring(response))
    return tree


def deep_search(search_list, lang="en", timeout=30):
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
        "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
        "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
        "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
        "xml": "http://www.w3.org/XML/1998/namespace",
    }
    codelist_list = []
    for row in search_list:
        dataflow_id = row["id"]
        try:
            tree = get_dimension_dataflows(dataflow_id, timeout=timeout)
        except MappingsError as e:
            print(e)
            codelist_list.append([])
            continue
        if tree is None:
            print("Warning: data for {dataflow_id} could not be retrieved. Skipping.")
            codelist_list.append([])
            continue
        cube_region = tree.find(".//structure:CubeRegion", namespaces)
        key_values = cube_region.findall(".//common:KeyValue", namespaces)

        for codelist in tree.findall(".//structure:Codelist", namespaces):
            codelist_name = codelist.find(
                f'.//common:Name[@xml:lang="{lang}"]', namespaces
            ).text

            for code in codelist.findall(".//structure:Code", namespaces):
                code_id = code.get("id")

                for idx, key_value in enumerate(key_values):
                    for value in key_value.findall("common:Value", namespaces):
                        if value.text == code_id:
                            codelist_list.append(
                                {
                                    "dimension_name": codelist_name,
                                    "dimension_value": code_id,
                                    "order": idx + 1,
                                }
                            )
                            break
        dict_list = format_dimensions(codelist_list)
        row["dataflow_dimensions"] = dict_list

    return search_list
