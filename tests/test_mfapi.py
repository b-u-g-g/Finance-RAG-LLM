"""
Unit tests for the MFAPI helper functions.

These functions are duplicated here so tests can run without importing app.py,
which accesses st.secrets at module level (requires a live Streamlit context).
"""
import unittest
from unittest.mock import patch, MagicMock

_MFAPI = "https://api.mfapi.in/mf"


# ── Replicated pure functions ─────────────────────────────────────────────────

def get_available_schemes(amc_name):
    import requests
    r = requests.get(f"{_MFAPI}/search", params={"q": amc_name}, timeout=10)
    r.raise_for_status()
    return {str(item["schemeCode"]): item["schemeName"] for item in r.json()}


def get_scheme_quote(scheme_code):
    import requests
    r = requests.get(f"{_MFAPI}/{scheme_code}/latest", timeout=10)
    r.raise_for_status()
    resp = r.json()
    meta = resp.get("meta", {})
    data = resp.get("data", [{}])
    return {
        "scheme_code": str(scheme_code),
        "scheme_name": meta.get("scheme_name", ""),
        "nav": data[0].get("nav", "") if data else "",
        **meta,
    }


def get_scheme_details(scheme_code):
    import requests
    r = requests.get(f"{_MFAPI}/{scheme_code}", timeout=10)
    r.raise_for_status()
    meta = r.json().get("meta", {})
    return {
        "scheme_code": str(scheme_code),
        "scheme_name": meta.get("scheme_name", ""),
        "fund_house": meta.get("fund_house", ""),
        "scheme_type": meta.get("scheme_type", ""),
        "scheme_category": meta.get("scheme_category", ""),
        **meta,
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestGetAvailableSchemes(unittest.TestCase):

    @patch("requests.get")
    def test_returns_dict_of_code_to_name(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [
            {"schemeCode": 120503, "schemeName": "SBI Bluechip Fund"},
            {"schemeCode": 120505, "schemeName": "SBI Small Cap Fund"},
        ]
        mock_get.return_value = mock_resp

        result = get_available_schemes("SBI")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["120503"], "SBI Bluechip Fund")
        self.assertEqual(result["120505"], "SBI Small Cap Fund")

    @patch("requests.get")
    def test_scheme_codes_are_strings(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"schemeCode": 100, "schemeName": "Test Fund"}]
        mock_get.return_value = mock_resp

        result = get_available_schemes("Test")

        self.assertIn("100", result)

    @patch("requests.get")
    def test_empty_results_returns_empty_dict(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        result = get_available_schemes("NoSuchAMC")

        self.assertEqual(result, {})

    @patch("requests.get")
    def test_correct_search_url_called(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        get_available_schemes("HDFC")

        mock_get.assert_called_once_with(
            f"{_MFAPI}/search", params={"q": "HDFC"}, timeout=10
        )


class TestGetSchemeQuote(unittest.TestCase):

    @patch("requests.get")
    def test_returns_nav_and_metadata(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "meta": {"scheme_name": "SBI Bluechip Fund", "fund_house": "SBI MF"},
            "data": [{"nav": "55.1234", "date": "08-03-2026"}],
        }
        mock_get.return_value = mock_resp

        result = get_scheme_quote("120503")

        self.assertEqual(result["scheme_code"], "120503")
        self.assertEqual(result["nav"], "55.1234")
        self.assertEqual(result["scheme_name"], "SBI Bluechip Fund")
        self.assertEqual(result["fund_house"], "SBI MF")

    @patch("requests.get")
    def test_empty_data_list_gives_empty_nav(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"meta": {}, "data": []}
        mock_get.return_value = mock_resp

        result = get_scheme_quote("999")

        self.assertEqual(result["nav"], "")

    @patch("requests.get")
    def test_scheme_code_is_string_in_result(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"meta": {}, "data": [{"nav": "10.0"}]}
        mock_get.return_value = mock_resp

        result = get_scheme_quote(120503)

        self.assertIsInstance(result["scheme_code"], str)
        self.assertEqual(result["scheme_code"], "120503")


class TestGetSchemeDetails(unittest.TestCase):

    @patch("requests.get")
    def test_returns_fund_metadata(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "meta": {
                "scheme_name": "SBI Bluechip Fund",
                "fund_house": "SBI Mutual Fund",
                "scheme_type": "Open Ended Schemes",
                "scheme_category": "Equity Scheme",
            }
        }
        mock_get.return_value = mock_resp

        result = get_scheme_details("120503")

        self.assertEqual(result["fund_house"], "SBI Mutual Fund")
        self.assertEqual(result["scheme_type"], "Open Ended Schemes")
        self.assertEqual(result["scheme_category"], "Equity Scheme")

    @patch("requests.get")
    def test_missing_meta_fields_return_empty_string(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"meta": {}}
        mock_get.return_value = mock_resp

        result = get_scheme_details("120503")

        self.assertEqual(result["scheme_name"], "")
        self.assertEqual(result["fund_house"], "")
        self.assertEqual(result["scheme_type"], "")
        self.assertEqual(result["scheme_category"], "")

    @patch("requests.get")
    def test_scheme_code_preserved_in_result(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"meta": {"scheme_name": "Test Fund"}}
        mock_get.return_value = mock_resp

        result = get_scheme_details("120503")

        self.assertEqual(result["scheme_code"], "120503")


if __name__ == "__main__":
    unittest.main()
