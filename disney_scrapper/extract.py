import requests

__base_url = 'https://disneyworld.disney.go.com/'
__default_headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'cache-control': 'no-cache',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
}


def get_resorts():
    response = requests.get(
        f'{__base_url}/wdpr-resorts-list-api/api/v1/resorts?storeId=wdw&resortGroup=CORE&region=us',
        headers = __default_headers
    )

    result = response.json()
    return result


def get_reservations(check_in_date, check_out_date, adult_count, child_count):
    body = {
        "storeId": "wdw",
        "checkInDate": check_in_date,
        "checkOutDate": check_out_date,
        "partyMix": { "adultCount": adult_count, "childCount": child_count, "nonAdultAges": [] },
        "accessible": False,
        "region": "us",
        "resortGroup": "CORE",
        "affiliations": ["STD_GST"]
    }
    response = requests.post(
        f'{__base_url}/wdpr-resorts-list-api/api/v1/resort-availability',
        headers = __default_headers,
        json = body
    )

    result = response.json()
    return result
