def apply_markup(quotes, markup_pct=15):
    for q in quotes:
        q["final_rate"] = round(q["rate"] * (1 + markup_pct / 100), 2)
        q["margin"] = round(q["final_rate"] - q["rate"], 2)
    return quotes
