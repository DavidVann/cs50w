import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "VTUIZDIx3LSTlXn1euBKg", "isbns":"9781632168146"})

info = res.json()
print(info)

print(info['books'][0]['ratings_count'])

try:
    bad_req = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "VTUIZDIx3LSTlXn1euBKg", "isbns":"as"})
    bad_req.raise_for_status()
except requests.exceptions.HTTPError:
    print("Bad request")

my_api = requests.get("http://127.0.0.1:5000/api/0553803700")

print(my_api.json())
