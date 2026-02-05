def generate_report(country, before, after):
    saved = before - after
    percent = (saved / before) * 100
    return saved, percent
