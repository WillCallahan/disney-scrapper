import os
from collections import Counter

from disney_scrapper.duplication_checker import filter_previously_checked


def _transform_resorts_and_reservations(resorts, reservations, max_price, exclude_resorts):
    flattened_data = list(filter(lambda i: 'offers' in i[1], reservations.get('resorts').items()))
    flattened_data = list(map(lambda r: {
        'resort_id': r[0], **r[1].get('offers', { }).get('best', { }),
        'price': r[1].get('offers', { }).get('best', { }).get('displayPrice', { }).get('basePrice', { }).get('subtotal',
                                                                                                             -1) },
                              flattened_data))
    flattened_data = list(filter(lambda r: max_price >= r['price'] > 0, flattened_data))
    joined_resorts = [{ **d, 'resort': resorts.get('resorts', { }).get(d['resort_id']) } for d in flattened_data]
    joined_resorts_filtered = list(filter(lambda r: not any([e in r.get('resort', { }).get('name') for e in
                                                             exclude_resorts]), joined_resorts))
    return joined_resorts_filtered


def _report_resort(availability):
    resort = availability.get('resort', { })
    resort_name = resort.get('name')
    price = availability.get('price')
    resort_type = resort.get('facets', { }).get('resortCategory', { })[0].get('value')
    return f'{os.linesep} - {resort_name}: ${price:,.2f} - {resort_type}'


def _frequency_report(all_availabilities):
    resort_types = [r.get('resort', { }).get('facets', { }).get('resortCategory', { })[0].get('value') for r in
                    all_availabilities]
    counter = Counter(resort_types)
    counts = [f'{os.linesep} - {c}: {counter[c]}' for c in counter]
    counts = ''.join(counts)
    return f'Overview: {counts}'


def _report_by_price(all_availabilities):
    reports = list(map(_report_resort, all_availabilities))
    resort_list = ''.join(reports)
    return f'Resorts: {resort_list}'


def _build_key_data_check(result: dict):
    return result.get('resort', { }).get('name', '')


def _get_price_data_check(result: dict):
    return result.get('price', 0)


def transform_to_message(resorts, reservations, max_price, exclude_resorts, start_date, end_date, dynamo_table_name):
    flattened_data = _transform_resorts_and_reservations(resorts, reservations, max_price, exclude_resorts)
    flattened_data = list(filter_previously_checked(flattened_data,
                                                    dynamo_table_name,
                                                    _build_key_data_check,
                                                    _get_price_data_check))
    if not flattened_data:
        return None
    report_by_price = _report_by_price(flattened_data)
    frequency_report = _frequency_report(flattened_data)
    message = f'''Max Price: {max_price}
Reservation Date: {start_date} - {end_date}
{frequency_report}

{report_by_price}'''
    return message
