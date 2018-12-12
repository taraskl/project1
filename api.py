import requests

def main():
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ubpONM2BPSrMnFHwGMn00w", "isbns": "9781632168146"})
    print(res.json())

if __name__ == "__main__":
    main()
