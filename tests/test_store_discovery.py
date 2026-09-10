from app.discovery.supported_retailers import normalize_retailer_name
def test_supported_retailer():
    assert normalize_retailer_name("Walmart") == "Walmart"


def test_supported_retailer_case_insensitive():
    assert normalize_retailer_name("  WALMART  ") == "Walmart"


def test_unsupported_retailer():
    assert normalize_retailer_name("Costco") is None