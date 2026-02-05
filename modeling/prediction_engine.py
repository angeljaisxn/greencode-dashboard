def predict_low_carbon_hours(df, country, threshold=200):
    subset = df[df["country"] == country]
    low_hours = subset[
        subset["carbon_intensity_gCO2_per_kWh"] < threshold
    ]["utc_hour"].unique()
    return sorted(low_hours)
