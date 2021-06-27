# Bench Rest Test for Deniz Aydin, June 26 2021

# references: https://www.nylas.com/blog/use-python-requests-module-rest-apis/

# could use JSON headers to determine count of transactions
# get data from json files until reaching end of transactions 
# and/or getting a 404 Server Error in page ping - 
# NTS: which is correct? Will probably go with 404 Error on page ping 


# need the GET method to read data from JSON files
# no authentication required (unlike an actual server/website)

# define libraries required to interact with the API
# had to install requests module via pip
import requests
from datetime import date
from datetime import datetime
import json
import numpy as np 
import pandas as pd 


# function to convert date to integer value for sorting. 
# Limitation: Does not take into account data from different months
# or number-of-days in a month
def to_integer(dt_time):
    # read date string, split at dashes
    # convert date string to integer value
    dt_time = dt_time.split("-")
    return 10000*int(dt_time[0]) + 100*int(dt_time[1]) + int(dt_time[2])

# flag is used to keep reading data until you get a 404 error
flag  = 0
# started numbering from zero, that was a mistake. 
# Limitation : code not robust to counts starting form 0.
num = 1
balance = 0
df = pd.DataFrame()

while (flag == 0):    
    try:
        webpage = 'https://resttest.bench.co/transactions/%d.json' % num
        response = requests.get(webpage)
        response.raise_for_status()

        # look at the content of the request itself with .json() method
        # json returns a dict, add to dataframe       
        # add data from each response to dataframe
        df = df.append(pd.DataFrame.from_dict(response.json()))
    # This code will run if there is a 4xx or 5xx error.    
    except requests.exceptions.HTTPError as error:
        print(error)
        flag = 1
    # is the server active?
    except requests.ConnectionError as error:
        print(error)
        flag = 1
    # did I complete the request in alloted time?
    except requests.Timeout as error:
        print(error)
        flag = 1
    # is there another issue? 
    except requests.exceptions.RequestException as error:
        print(error)
        flag = 1
    # could handle too many redirects here, but I don't expect it to be necessary for this
    num = num +1

# make transactions into a list so that you can go into the elements
transactions = df['transactions'].tolist()   

# make a list of tuples (date as integer, amount of transaction)

date_amount =  [(to_integer(item['Date']),item['Amount']) for item in transactions]

# sort based on date as integer, then get the sums and print with date

date_amount.sort(key = lambda x: x[0])


# get earliest date as integer and set benchmark date
prev_date = date_amount[0][0]
# determine the last date
last_date = date_amount[len(date_amount)-1][0]


# we don't care about missing dates because we're usig indices

for idx in range(len(date_amount)):
    cur_date = date_amount[idx][0]
    if (prev_date != cur_date):
        print(str(prev_date)[0:4] + '-' + str(prev_date)[4:6] + '-' + str(prev_date)[6:8] +' %.2f' % balance)
        # if last date, print the result as well
        if (cur_date == last_date):
            balance = balance + float(date_amount[idx][1])    
            print(str(cur_date)[0:4] + '-' + str(cur_date)[4:6] + '-' + str(cur_date)[6:8]+' %.2f' % balance)
        prev_date = cur_date
        balance = balance + float(date_amount[idx][1])
    else:
        balance = balance + float(date_amount[idx][1])

# authentication - is this required? NTS: no. Skipped this part. 
# if required, one can pass the username and password to the endpoint as HTTP basic authentication
# same as typing in your credentials on a website

# you can also use OAuth, where you log in through a provider that returns a token representing the UN/PW combination
# once you have this token, you use it as a bearer (NTS: what does this mean?) in the request header

# this is more secure than sending the UN/PW combination to the endpoint

# session objects, NTS: do I need these? Did not use for this code.  
# needed if making multiple requests in a single session, like access tokens
# but also several webpages? Then I need to create a session and end it when I get my 404 error

# managing session cookies can provide a nice performance increase because you don't need a new cnx for each request

# handling errors
# 1xx informational - not likely to need it in python requests
# 2xx successful - can use it to verify existence of data before acting on it
# 3xx redirection - additional action required: proxy or different endpt. 
# 4xx client error -  lack of authorization, forbidden access, disallowed methods, nonexistent resource
# 5 xx server error - API provider needs to resolve this


