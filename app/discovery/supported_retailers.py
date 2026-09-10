SUPPORTED_RETAILER_ALIASES = {
    "real canadian superstore": "Real Canadian Superstore",
    "superstore": "Real Canadian Superstore",

    "walmart": "Walmart",
    "walmart supercentre": "Walmart",

    "save-on-foods": "Save-On-Foods",
    "save on foods": "Save-On-Foods"
}


def normalize_retailer_name(name: str) -> str | None:
    key = name.strip().lower()
    return SUPPORTED_RETAILER_ALIASES.get(key)