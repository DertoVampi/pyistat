from pyistat import get, search
import pandas as pd


### Test single calls

# data = search.get_all_dataflows(timeout=90)
# all_df = pd.DataFrame(data)

search_data = search.search_dataflows("Tasso di Disoccupazione", lang="it", mode="deep", timeout=60)
df = pd.DataFrame(search_data)

# Search works!

# try_df = get.get_dimensions("163_247")
# try_df_2 = pyistat.get.get_dimensions("163_156_DF_DCCN_SQCQ_3")

### Test multiple calls
test_data = get.get_data("163_156_DF_DCCN_SQCQ_3", dimensions=["","","","","",""], start_period=2025, debug_url=True)
test_df = pd.DataFrame(test_data)

pil_list = get.get_data(
    "163_156_DF_DCCN_SQCQ_3",
    freq="Q",
    correz="Y",
    val="G4",
    timeout=120,
    start_period="2025"
)
pil_df = pd.DataFrame(pil_list)
# Crescita PIL
pil_growth_df = get.get_data(
    "163_156_DF_DCCN_SQCQ_2",
    dimensions=["Q", "IT", "B1GQ_B_W2_S1", "GO1", "Y", ""],
    force_url=True,
    timeout=120,
)
# Disoccupazione
unemployment_df = get.get_data(
    "151_874_DF_DCCV_TAXDISOCCUMENS1_1",
    dimensions=["", "", "", "N", "9", "Y15-74", ""],
    timeout=180,
)
# Inflazione
inflation_df = get.get_data(
    "167_742",
    dimensions=["A", "IT", "", "4", "00"],
    timeout=120,
)
# Clima di fiducia delle imprese
trust_df = get.get_data(
    "6_64_DF_DCSC_IESI_2",
    dimensions=["", "", "", "", ""],
    timeout=120,
)


# Costi energia
fuel_energy_df = get.get_data(
    "168_760_DF_DCSP_IPCA1B2015_2",
    dimensions=["", "", "", "4", "ENRGY_5DG"],
    force_url=True,
    timeout=120,
)
energy_df = get.get_data(
    "168_760_DF_DCSP_IPCA1B2015_2",
    dimensions=["", "", "", "4", "FUELS_5DG"],
    force_url=True,
    timeout=120,
)