import time
import requests

# CSFLOAT ------------------------------------
# Global variable to store the current cheapest price
price_list = [float('inf')] * 5
notiCount = -1

# API endpoint 
url = "https://csfloat.com/api/v1/listings"

# API key 
with open('apikeycs.txt', 'r') as file:
    api_key_cs = file.read().rstrip()
headers = {
    "Authorization": api_key_cs  
}

# Define the query parameters
params = {
    "page": 0,                   
    "limit": 5,                 # Number of listings to return (max 50)
    "sort_by": "lowest_price",   # Sorting criteria (e.g., "lowest_price", "highest_price", etc.)
    "category": 0,               # Category (e.g., 0 = any, 1 = normal, etc.)
    "min_float": 0.45,            # Only include listings with a float higher than this (optional)
    "paint_index": 10038,
    "max_float": 0.8,            # Only include listings with a float lower than this (optional)
    "type": "buy_now"            # Filter by type (either 'buy_now' or 'auction')
}

"""
    Check for new cheapest price
"""
def check_price():
    global price_list  # Use the global price_list variable
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        print("Request was successful.")
        response_json = response.json()
        cheapest = []

        # Get the price of the first 5 items
        for i in range(params["limit"]):
            currprice = response_json['data'][i]['price'] / 100  # Convert to dollars
            floatVal = response_json['data'][i]['item']['float_value']
            floatVal = round(floatVal, 5)
            cheapest.append((currprice,floatVal))

        # Check if any of the 5 values have changed
        if cheapest != price_list:
            print("Price changes detected.")
            # Send push notification
            send_notification(cheapest)
            # Update the global price list
            price_list = cheapest
            # Write newest 5 prices to a text file (also does it once at start)
            with open("cheapest_prices.txt", "w") as f:
                for price, floatVal in cheapest:
                    f.write(f"Price: ${price:.2f}, Float: {floatVal}\n")
        else:
            print("No price changes detected.")

    else:
        print(f"Error {response.status_code}: {response.text}")


# Pushover ----------------------

# API keys
with open('apikeyp.txt', 'r') as file:
    api_key_p = file.read().rstrip()

with open('apikeypuser.txt', 'r') as file:
    api_key_u = file.read().rstrip()

def send_notification(cheapest_price):
    price_message = "\n".join([f"Price: ${price:.2f}, Float: {floatVal}\n" for price, floatVal in cheapest_price])

    data = {
        "token": api_key_p,
        "user": api_key_u,
        "message": price_message,  # Updated to include all prices
        "title": "Price Drop",  
        "priority": 0, 
        "sound": "pushover",  
    }

    # Send notification
    response = requests.post("https://api.pushover.net/1/messages.json", data=data)

    if response.status_code == 200:
        global notiCount 
        notiCount += 1
        print("Notification sent successfully!")
    else:
        print(f"Failed to send notification: {response.status_code}, {response.text}")

# Main --------------------------
count = 0
while True:
    check_price()
    print("Time Running: " + str(count) + " minutes." + " || Notifications: " + str(notiCount))  
    print("Waiting for 30 seconds...\n")
    count += 0.5
    time.sleep(30)  