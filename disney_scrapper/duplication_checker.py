import boto3
from typing import Callable
from decimal import Decimal


def _swap_price_in_dynamo(table_name, partition_key, new_price):
    """
    Swaps the new price with the price in dynamo, returning the dynamo price

    :param table_name: Name of the Dynamo table
    :param partition_key: Partition Key to check
    :param new_price: New Price to Swap
    :return: None if there is no price in Dynamo or the old price from Dynamo
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)  # Replace with your actual table name

    try:
        response = table.get_item(Key = { 'resort_key': partition_key })
        old_price = response.get('Item', { }).get('price')

        table.update_item(
            Key = { 'resort_key': partition_key },
            UpdateExpression = 'SET price = :val',
            ExpressionAttributeValues = { ':val': Decimal(new_price) }
        )

        return old_price if not old_price else float(old_price)
    except Exception as e:
        print(f'Error fetching item from dynamo: {e}')
        return None


def filter_previously_checked(results: list[dict],
                              dynamo_table_name: str,
                              key_picker_func: Callable[[dict], str],
                              price_getter_func: Callable[[dict], float]):
    for result in results:
        key = key_picker_func(result)
        new_price = price_getter_func(result)
        old_price = _swap_price_in_dynamo(dynamo_table_name, key, new_price)
        if old_price is None or new_price < old_price:
            print(f'The price has decreased {key=} {new_price=} {old_price=}')
            yield result
        else:
            print(f'The price has not decreased {key=} {new_price=} {old_price=}')
