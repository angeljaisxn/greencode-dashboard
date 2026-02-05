import pandas as pd

def load_global_data():
    df = pd.read_csv("data/global_simulated_195_countries_30days.csv")
    return df
