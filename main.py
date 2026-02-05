
# from ingestion.load_data import load_global_data
# from analytics.carbon_metrics import calculate_emission
# from analytics.country_analysis import average_country_intensity
# from modeling.prediction_engine import predict_low_carbon_hours
# from scheduling.policy_engine import apply_policy

# ENERGY_PER_TASK = 0.5  # kWh

# df = load_global_data()
# country = "India"

# avg_intensity = average_country_intensity(df, country)
# normal_emission = calculate_emission(avg_intensity, ENERGY_PER_TASK)

# low_hours = predict_low_carbon_hours(df, country)
# decision = apply_policy(5, low_hours)

# if decision == "EXECUTE_NOW":
#     green_emission = normal_emission * 0.6
# else:
#     green_emission = normal_emission

# print("Country:", country)
# print("Normal Emission:", normal_emission, "gCO2")
# print("Green Emission:", green_emission, "gCO2")
# print("Carbon Saved:", normal_emission - green_emission, "gCO2")


from ingestion.load_data import load_global_data
from analytics.carbon_metrics import calculate_emission
from analytics.country_analysis import average_country_intensity
from modeling.prediction_engine import predict_low_carbon_hours
from scheduling.policy_engine import apply_policy

ENERGY_PER_TASK = 0.5  # kWh

df = load_global_data()

country = input("Enter country name: ")

avg_intensity = average_country_intensity(df, country)
normal_emission = calculate_emission(avg_intensity, ENERGY_PER_TASK)

low_hours = predict_low_carbon_hours(df, country)
decision = apply_policy(5, low_hours)

if decision == "EXECUTE_NOW":
    green_emission = normal_emission * 0.6
else:
    green_emission = normal_emission

print("\nCountry:", country)
print("Normal Emission:", round(normal_emission, 2), "gCO2")
print("Green Emission:", round(green_emission, 2), "gCO2")
print("Carbon Saved:", round(normal_emission - green_emission, 2), "gCO2")
