import googlemaps
import pandas as pd
import time
import sys
import json

def retrieve_places():
    # print(sys.argv[1])
    # print('test')
    print(location_query)
    location = client.geocode(location_query)[0]['geometry']['location']

    results = client.places(query = query,
                                location = location,
                                radius=distance,

    )

    status = results['status']

    print('Status: ' + status)

    if status == 'ZERO_RESULTS':
        #TODO Add func
        print('there were zero results!')


    results_df = pd.DataFrame(results['results'])

    while 'next_page_token' in results and len(results_df.index) < results_to_find:
        print('retrieving next page')
        print('starting delay...')
        time.sleep(next_page_delay)
        print('delay complete')
        token = results['next_page_token']
        
        results = client.places(query = query,
                                location = location,
                                radius=distance,
                                page_token = token
        )   

        if results['status'] == 'ZERO_RESULTS':
            print('next page led to zero results!')
            break
        
        next_results_df = pd.DataFrame(results['results'])
        results_df = results_df.append(next_results_df)
        print('Retrieved ' + str(len(next_results_df.index)) + ' additional results')


    results_df.reset_index(drop=True, inplace=True)

    print('Completed retrieving results')

    return results_df

def format_results(df):
    cols_to_remove = ['business_status', 'geometry', 'icon', 'icon_background_color', \
                      'icon_mask_base_uri', 'opening_hours', 'photos', 'plus_code', 'reference', \
                      'types' ]
                      
    df.drop(cols_to_remove, axis=1, inplace=True)
    
    print('Completed formatting results!')

    return df

def init_client(api_key):
    global client
    client = googlemaps.Client(key=api_key)


# returns new dataframe with updated data
def add_place_details_to_place(place_id, df):
    place_details = client.place(place_id)['result']

    phone = place_details['formatted_phone_number'] \
        if 'formatted_phone_number' in place_details \
            else ''

    website = place_details['website'] \
        if 'website' in place_details \
            else ''

    index = df.index[df['place_id'] == place_id].tolist()[0]

    df.at[index, 'phone'] = phone
    df.at[index, 'website'] = website

    print('retrieving place details')

    return df

args = sys.argv

# Location
# Query
# Distance (miles)
# results to find
# delay

f = open('config.json')
config = json.load(f)

location_query = '20550 Maxim Pkwy, Orlando, FL 32833'
query = 'Realtor'
distance = 10
results_to_find = 20
api_key = config["API_KEY"] 
# AIzaSyClJgh0MhdAeOIX4yEuSqqGXw3fGhCyi6E
#TODO add api_key dynamically
next_page_delay = 1.5

if(len(args) > 1):
    location_query = args[1]
    query = args[2]
    distance = int(args[3])
    results_to_find = int(args[4])
    next_page_delay = float(args[5]) if len(args) >= 6 else 2.5

init_client(api_key)

df = retrieve_places()

for row in df.itertuples():
    place_id = row.place_id
    df = add_place_details_to_place(place_id, df)

format_results(df)

print('process complete.')

df.index.name = 'Index'
df.to_csv('results.csv')

print('results saved.')

# EX. place_searching.py "Fort Myers" "Businesses" 10 160 1.5