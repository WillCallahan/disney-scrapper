import os

from disney_scrapper.extract import get_reservations, get_resorts
from disney_scrapper.load import load_to_sns
from disney_scrapper.transform import transform_to_message


def handle_request(request, resorts):
    check_in_date = request.get('check_in_date', None)
    check_out_date = request.get('check_out_date', None)
    adult_count = request.get('adult_count', 0)
    child_count = request.get('child_count', 0)
    max_price = request.get('max_price', None)
    exclude_resorts = request.get('exclude_resorts', [])
    reservations = get_reservations(check_in_date, check_out_date, adult_count, child_count)
    message = transform_to_message(resorts, reservations, max_price, exclude_resorts, check_in_date, check_out_date)
    return message


def handle_all_requests(requests):
    sns_topic = os.environ.get('SNS_TOPIC', 'arn:aws:sns:us-east-1:157482313302:disney-notification-topic')
    resorts = get_resorts()
    for request in requests:
        message = handle_request(request, resorts)
        if not message:
            print(f'No reservations found {request=}')
            continue
        load_to_sns(message, 'Disney Reservation Found', sns_topic)


def lambda_handler(params, *args):
    try:
        print(f'Executing lambda function {params=} {args=}')
        handle_all_requests(params)
        print('Execution completed')
    except Exception as e:
        print(e)



def __test_lambda_handler():
    params = [
        {
            "check_in_date": "2025-04-04",
            "check_out_date": "2025-04-05",
            "adult_count": 2,
            "child_count": 0,
            "max_price": 300,
            "exclude_resorts": ["Art of Animation"]
        }
    ]
    lambda_handler(params)


if __name__ == '__main__':
    __test_lambda_handler()
