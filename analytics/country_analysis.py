def average_country_intensity(df, country):
    country_df = df[df["country"] == country]
    return country_df["carbon_intensity_gCO2_per_kWh"].mean()
