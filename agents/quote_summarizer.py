import openai
from dotenv import load_dotenv
import os

load_dotenv()

# Set your API key (or use dotenv or environment variable setup)
client = openai.OpenAI(api_key=os.getenv("OPENAI_KEY"))

def generate_quote_summary(data, quotes):
    origin = data["origin"]
    destination = data["destination"]
    weight = data["weight"]
    freight_class = data["freight_class"]
    mode = data["mode"]
    description = data.get("description", "")
    
    # Format vendor quotes
    quote_lines = "\n".join(
        f"- {q['vendor']}: PHP {q['final_rate']:,} (Base: {q['rate']}, Margin: {q['margin']})"
        for q in quotes
    )

    prompt = f"""
Summarize the freight quote below in a professional paragraph.

**Route**: {origin} → {destination}  
**Weight**: {weight} lbs  
**Freight Class**: {freight_class}  
**Mode**: {mode}  
**Cargo Description**:  
{description}

**Vendor Quotes**:  
{quote_lines}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes freight quote details."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
