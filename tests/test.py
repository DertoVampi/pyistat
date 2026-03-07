from pyistat import get, search


### Test single calls

data = search.get_all_dataflows(timeout=90)
# all_df = pd.DataFrame(data)

search_data = search.search_dataflows("Tasso di Disoccupazione", lang="it", mode="deep", timeout=60, returned="csv")


### Search works!

try_df = get.get_dimensions("163_247", returned="csv")
try_df_2 = get.get_dimensions("163_156_DF_DCCN_SQCQ_3", returned="csv")

### Test multiple calls
test_data = get.get_data(
    "163_156_DF_DCCN_SQCQ_3",     
    freq="Q",
    correz="Y",
    val="G4")
# test_df = pd.DataFrame(test_data)

pil_list = get.get_data(
    "163_156_DF_DCCN_SQCQ_3",
    freq="Q",
    correz="Y",
    val="G4",
    timeout=120,
    start_period="2025",
    returned="csv"
)
# pil_df = pd.DataFrame(pil_list)

# Crescita PIL
pil_growth_df = get.get_data(
    "163_156_DF_DCCN_SQCQ_2",
    dimensions=["Q", "IT", "B1GQ_B_W2_S1", "GO1", "Y", ""],
    timeout=120,
)
# pil_growth_data = pd.DataFrame(pil_growth_df)

# Disoccupazione
unemployment_df = get.get_data(
    "151_874_DF_DCCV_TAXDISOCCUMENS1_1",
    dimensions=["", "", "", "", "", "", "2022M2G1"],
    timeout=180,
)
# unemployment_data = pd.DataFrame(unemployment_df)

# Inflazione
inflation_df = get.get_data(
    "167_742",
    dimensions=["A", "IT", "", "4", "00"],
    timeout=120,
    returned="csv"
)
# inflation_data = pd.DataFrame(inflation_df)

# Clima di fiducia delle imprese
trust_df = get.get_data(
    "6_64_DF_DCSC_IESI_2",
    dimensions=["", "", "", "", ""],
    timeout=120,
)
# trust_data = pd.DataFrame(trust_df)


# Costi energia
fuel_energy_df = get.get_data(
    "168_760_DF_DCSP_IPCA1B2015_2",
    dimensions=["", "", "", "4", "ENRGY_5DG"],
    force_url=True,
    timeout=120,
)
# fuel_energy_data = pd.DataFrame(fuel_energy_df)

energy_df = get.get_data(
    "168_760_DF_DCSP_IPCA1B2015_2",
    dimensions=["", "", "", "4", "FUELS_5DG"],
    force_url=True,
    timeout=120,
)

# energy_data = pd.DataFrame(energy_df)

for _ in range(50): # Sorry ISTAT!
    counter = _
    pil_growth_df = get.get_data(
        "163_156_DF_DCCN_SQCQ_2",
        dimensions=["Q", "IT", "B1GQ_B_W2_S1", "GO1", "Y", ""],
        timeout=50,
        test_rows=1,
    )