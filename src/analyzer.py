import json
from typing import Optional
import anthropic
from . import config


def analyze_pair(brand: dict, store: dict, client: Optional[anthropic.Anthropic] = None) -> dict:
    """Analyze a brand against a store using demographic + store data.

    Args:
        brand: dict with keys: name, category, description, target_consumer,
                               proof_points, distribution_stage
        store: dict — a row from enriched_stores.csv as a dict
    """
    if client is None:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def fmt(val, suffix=""):
        if val is None or val == "" or str(val).strip() in ("nan", ""):
            return "N/A"
        try:
            return f"{float(val):,.1f}{suffix}"
        except (ValueError, TypeError):
            return str(val)

    prompt = f"""Analyze this brand against the following store location:

BRAND PROFILE
Name: {brand.get("name", "")}
Category: {brand.get("category", "")}
Description: {brand.get("description", "")}
Target consumer: {brand.get("target_consumer", "")}
Proof points / traction: {brand.get("proof_points", "")}
Current distribution stage: {brand.get("distribution_stage", "")}

STORE PROFILE
Store name: {store.get("store_name", "")}
Banner: {store.get("banner_name", "")}
Type: {store.get("type", "")}
Location: {store.get("city", "")}, {store.get("state", "")} {store.get("zipcode", "")}
Parent chain store count: {fmt(store.get("parent_store_count"))}
Sales volume (location): {fmt(store.get("sales_volume_location"), "K")}
Employee size (location): {fmt(store.get("employee_size_location"))}

TRADE AREA DEMOGRAPHICS
Median household income: ${fmt(store.get("median_hh_income"))}
Avg per capita income: ${fmt(store.get("avg_per_capita_income"))}
% income $100k+: {fmt(store.get("pct_income_100k_plus"), "%")}
% income $200k+: {fmt(store.get("pct_income_200k_plus"), "%")}
Total population: {fmt(store.get("total_population"))}
Population density: {fmt(store.get("pop_density"))} per sq mi
% age 25–34: {fmt(store.get("pct_age_25_34"), "%")}
% age 35–44: {fmt(store.get("pct_age_35_44"), "%")}
% bachelor's degree or higher: {fmt(store.get("pct_bachelors_plus"), "%")}
% married couple households: {fmt(store.get("pct_married_couple"), "%")}
% owner occupied: {fmt(store.get("pct_owner_occupied"), "%")}"""

    response = client.messages.create(
        model=config.MODEL,
        max_tokens=1024,
        system=config.SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)
