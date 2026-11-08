"""Live HTTP verification script testing running FastAPI server."""

import json
import httpx

BASE_URL = "http://127.0.0.1:8000"

endpoints = [
    ("1. Health Check", "/api/health"),
    ("2. Product Listing (page=1, size=2)", "/api/products?page=1&page_size=2"),
    ("3. Product Search (q=Fire TV)", "/api/products/search?q=Fire%20TV&page=1&page_size=2"),
    ("4. Product Details (B075X8471B)", "/api/products/B075X8471B"),
    ("5. Product Reviews (B075X8471B, size=2)", "/api/products/B075X8471B/reviews?page=1&page_size=2"),
    ("6. Rating Statistics (B075X8471B)", "/api/products/B075X8471B/statistics"),
    ("7. Dashboard Overview", "/api/dashboard/overview"),
    ("8. 404 Error Handling", "/api/products/NON_EXISTENT_ID"),
    ("9. OpenAPI Specs", "/openapi.json"),
]


def run_live_tests():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        for name, path in endpoints:
            print("=" * 80)
            print(f"TESTING ENDPOINT: {name} [{path}]")
            print("-" * 80)
            resp = client.get(path)
            print(f"Status Code: {resp.status_code}")
            try:
                data = resp.json()
                if path == "/openapi.json":
                    print(f"OpenAPI Title: {data.get('info', {}).get('title')}")
                    print(f"Available API Paths: {list(data.get('paths', {}).keys())}")
                else:
                    formatted = json.dumps(data, indent=2)
                    if len(formatted) > 1000:
                        print(formatted[:1000] + "\n... [truncated for display]")
                    else:
                        print(formatted)
            except Exception as e:
                print("Raw text:", resp.text[:300])
            print("=" * 80 + "\n")


if __name__ == "__main__":
    run_live_tests()

