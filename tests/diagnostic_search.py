
import requests
import json
import sys

# NSE
NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.nseindia.com/'
}

def test_nse(q):
    print(f"\n--- Testing NSE for: {q} ---")
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)
    url = f"https://www.nseindia.com/api/search/autocomplete?q={q}"
    r = session.get(url, headers=NSE_HEADERS, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        symbols = data.get('symbols', [])
        print(f"Found {len(symbols)} symbols")
        for s in symbols[:5]:
            print(f"  {s.get('symbol')} - {s.get('name')}")
    else:
        print(f"Error: {r.text[:200]}")

# BSE
BSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.bseindia.com/'
}

def test_bse(q):
    print(f"\n--- Testing BSE for: {q} ---")
    url = f"https://api.bseindia.com/BseIndiaAPI.api/GetScripData/w?SearchVal={q}"
    r = requests.get(url, headers=BSE_HEADERS, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        scripList = data.get('scripList', [])
        print(f"Found {len(scripList)} scrips")
        for s in scripList[:5]:
            print(f"  {s.get('scrip_cd')} - {s.get('scrip_nm')}")
    else:
        print(f"Error: {r.text[:200]}")

queries = ["triveni turbine", "triveni", "triturbine"]
for q in queries:
    test_nse(q)
    test_bse(q)
