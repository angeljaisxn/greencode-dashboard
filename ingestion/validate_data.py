def validate(df):
    if df.empty:
        raise ValueError("Dataset is empty")
    return True
