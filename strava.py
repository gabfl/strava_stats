import os
from datetime import date
from datetime import datetime, timedelta
import json

import requests
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable

first_day_of_week = 'monday'  # acceptable values: 'sunday', 'monday'
acceptable_activity_types = {'Run', 'VirtualRide', 'Ride'}
activity_type_mapping = {'VirtualRun': 'Run', 'VirtualRide': 'Ride'}


def read_env_variables():
    """ Read Strava secrets from env variables """

    try:
        return os.environ['STRAVA_CLIENT_ID'], os.environ['STRAVA_CLIENT_SECRET'], os.environ['STRAVA_USER_REFRESH_TOKEN']
    except KeyError:
        raise RuntimeError(
            'The following environments variables need to be set: STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET & STRAVA_USER_REFRESH_TOKEN')


def get_access_token(client_id, client_secret, refresh_token):
    """ Return a user short-lived access token """

    r = requests.post('https://www.strava.com/api/v3/oauth/token',
                      data={
                          'client_id': client_id,
                          'client_secret': client_secret,
                          'refresh_token': refresh_token,
                          'grant_type': 'refresh_token'
                      },
                      headers={
                          'accept': 'application/json'
                      })

    if r.status_code == 200:
        body = r.json()

        return body['access_token']
    else:
        raise RuntimeError(r.text)


def get_activities(client_id, client_secret, access_token):
    """ Return list of Strava activities """

    page = 1
    activities = []

    while True:
        r = requests.get('https://www.strava.com/api/v3/athlete/activities?after=%s&page=%d&per_page=50' % (get_epoch(), page),
                         headers={
            'accept': 'application/json',
            'Authorization': f"Bearer {access_token}"
        })

        # Increment page
        page += 1

        if r.status_code == 200:
            # No more pages
            if len(r.json()) == 0:
                break

            # Append activities
            for item in r.json():
                if item['type'] in acceptable_activity_types:  # Only map run and bike activities
                    activities.append({
                        'type':  activity_type_mapping[item['type']] if activity_type_mapping.get(item['type']) else item['type'],
                        'distance': item['distance'],
                        'start_date_local': item['start_date_local']
                    })
        else:
            raise RuntimeError(r.text)

    return activities


def sort_activities(activities):
    """ Sort user activities """

    current_week = get_week_number(datetime.now())
    previous_week = get_week_number(datetime.now() - timedelta(days=7))
    current_month = get_month_number(datetime.now())
    previous_month = get_month_number(datetime.now() - relativedelta(months=1))

    activities_sorted = {}
    for activity in activities:
        activity_type = activity['type']
        distance = activity['distance']
        start_date_local = activity['start_date_local']
        start_date_local_dt = datetime.strptime(
            start_date_local, '%Y-%m-%dT%H:%M:%SZ')

        if not activities_sorted.get(activity_type):
            activities_sorted[activity_type] = {
                'current_week': 0,
                'previous_week': 0,
                'current_month': 0,
                'previous_month': 0
            }

        # Add to weekly total
        if get_week_number(start_date_local_dt) == current_week:
            activities_sorted[activity_type]['current_week'] += distance
        elif get_week_number(start_date_local_dt) == previous_week:
            activities_sorted[activity_type]['previous_week'] += distance

        # Add to monthly total
        if get_month_number(start_date_local_dt) == current_month:
            activities_sorted[activity_type]['current_month'] += distance
        elif get_month_number(start_date_local_dt) == previous_month:
            activities_sorted[activity_type]['previous_month'] += distance

    # print(activities_sorted)
    return activities_sorted


def get_week_number(dt):
    """ Return week number """

    return dt.strftime('%W' if first_day_of_week.lower() == 'monday' else '%U')


def get_month_number(dt):
    """ Return current month number """

    return dt.strftime('%m')


def get_epoch():
    """
        Returns epoch of first of the month
        Bug: currently seems to return epoch at local tz instead of UTC !?
    """

    return (date.today().replace(day=1) - relativedelta(months=1)).strftime('%s')


def distance_to_miles(distance):
    """ Distance in meters to miles """

    return str(round(distance / 1609.3, 1)) + ' mi'


def print_table(activities_sorted):
    """ Print user friendly table """

    x = PrettyTable()

    x.field_names = ['Type', 'This week',
                     'Last week', 'This month', 'Last month']
    x.align['This week'] = "r"
    x.align['Last week'] = "r"
    x.align['This month'] = "r"
    x.align['Last month'] = "r"

    x.add_row([
        'Run',
        distance_to_miles(activities_sorted['Run']['current_week']),
        distance_to_miles(activities_sorted['Run']['previous_week']),
        distance_to_miles(activities_sorted['Run']['current_month']),
        distance_to_miles(activities_sorted['Run']['previous_month'])
    ])
    x.add_row([
        'Bike',
        distance_to_miles(activities_sorted['Ride']['current_week']),
        distance_to_miles(activities_sorted['Ride']['previous_week']),
        distance_to_miles(activities_sorted['Ride']['current_month']),
        distance_to_miles(activities_sorted['Ride']['previous_month'])
    ])

    print(x)


def main():
    # Read Strava secrets from env
    client_id, client_secret, refresh_token = read_env_variables()

    # Get user short-lived access token
    access_token = get_access_token(client_id, client_secret, refresh_token)
    # print(access_token)

    # Retrieve user activities
    activities = get_activities(client_id, client_secret, access_token)
    # print(json.dumps(activities))

    # Sort and group user activities
    activities_sorted = sort_activities(activities)

    # Print table
    print_table(activities_sorted)


main()
