from pyistat import get, search
import polars as pl

data = search.search_dataflows("Prodotto Interno Lordo", lang="it", mode="deep") 
data_df = pl.DataFrame(data)