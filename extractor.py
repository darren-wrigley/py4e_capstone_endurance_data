"""
read event_urls.csv and collect event data - store into sqlite database
"""
import ssl
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import re
import sqlite3
import requests
from requests_html import HTMLSession
import json

session = HTMLSession()
url_filename = 'event_urls.csv'

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('raw_racedata.sqlite')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS racedata
(id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, event, year INTEGER,
division TEXT, place INTEGER, athlete TEXT, time TEXT)''')

division_id = 0
course_id = 0
event_id = 0

error_urls = []


def get_page_content(url):
    print(f"extracting url/page: {url}")
    try:
        # Open with a timeout of 30 seconds
        # html_data = requests.get(url, verify=False)
        document = urllib.request.urlopen(url, None, 30, context=ctx)
        text = document.read().decode()
        # r = session.get(url)
        if document.getcode() != 200 :
            print("Error code=",document.getcode(), url)
            return None
    except Exception as e:
        print("Unable to retrieve or parse page",url)
        print("Error",e)
        return

    print("\t", document.getcode(), url,len(text))
    # count = count + 1

    # parse the course id
    id_data = re.findall("\/Event\/(.*)\/Course\/(.*)\/Division\/(.*)\/Results", url)
    event = id_data[0][0]
    course = id_data[0][1]
    division = id_data[0][2]

    return text, event, course, division


def parse_athlinks_page(url, page_content, event_id, course_id, division_id):
    # use BS4 to get page data
    # print(page_content)
    soup = BeautifulSoup(page_content, 'html.parser')
    # event name?
    event = None
    division = None
    year = None
    # get the first h3 (the event name)
    for h in soup.find_all('h1'):
        print(h.text)
        if event is None:
            event = h.text

    # get the gender
    for h in soup.find_all('div', {'class': 'MuiInputBase-root MuiInput-root MuiInput-underline MuiInputBase-formControl MuiInput-formControl'}):
        # print(h)
        # print(h.previous)
        # print(h.text)
        if h.previous == 'Division':
            division = h.text
        if h.previous == 'Event Date':
            # parse the year from h
            try:
                year = int(re.findall('[0-9]{4}', h.text)[0])
            except:
                print("cannot extract year from date: ", h.text)


    print(f"\tEvent={event}")
    print(f"\tDivision={division}")
    print(f"\tyear={year}")

    # if event name is null - then call this
    # https://www.athlinks.com/athlinks/Events/Api/Merged/732163 & look for masterName in result:
    if event is None:
        # call a webservice (found by monitoring a page load/refresh in chrome)
        # edge case (intermittent???) - call a service to extract the event data
        event_url = f"https://www.athlinks.com/athlinks/Events/Api/Merged/{event_id}"
        print("event data not found --  calling event api", event_url)
        event_handle = urllib.request.urlopen(event_url, None, 30, context=ctx)
        event_data = event_handle.read().decode()
        print("event_data", event_data)
        event_json = json.loads(event_data)
        event = event_json['result']['masterName']
        print(event_json['result']['masterName'])
        year = int(event_json['result']['startTime'][:4])
        print(event_json['result']['startTime'][:4])


    # get the rows of results from the page
    res_count = 0
    # eventResults_1575400
    # for result in soup.find_all('div', {'class': ['mx-0', 'link-to-irp']}):
    # eventResults_975877
    event_html_id = 'eventResults_' + division_id
    print(f"\tsearch for event table\'{event_html_id}'")
    for result in soup.find_all('div', {'id': 'eventResults_' + division_id}):
        for result_row in result.findChildren('div', {'class': ['mx-0', 'link-to-irp']}):
            res_count += 1
            ath_name = None
            ath_time = None
            # each row processed here
            # print(res_count, result)
            # athsoup = BeautifulSoup(result, 'html.parser')
            # ath_disp = athsoup.find_all('athName')
            # print(ath_disp)
            a_name = result_row.findChildren('a', {'class': 'athName'})
            # print(a_name)
            if len(a_name) >=1:
                ath_name = a_name[0].text
            a_time = result_row.findChildren('div', {'class': 'col-2'})
            if len(a_time) >=1:
                ath_time = a_time[0].text

            # print(f"{event}, {year}, {division}, {res_count}, {ath_name}, {ath_time}")
            cur.execute('''INSERT OR IGNORE INTO racedata (url, event, year, division,  place, athlete, time)
                        VALUES ( ?, ?, ?, ?, ?, ?, ? )''', ( url, event, year, division, res_count, ath_name, ath_time))

    print(res_count, " rows found")
    if res_count == 0:
        # try using a different url - that get the actual data as json
        new_url = f"https://results.athlinks.com/event/{event_id}?eventCourseId={course_id}&divisionId={division_id}&from=0&limit=50"
        print("\treading alt url", new_url)
        new_resp = requests.get(new_url)
        print(new_resp.status_code)
        if new_resp.status_code == 200:
            res_json = new_resp.json()
            # print(res_json[0])
            for iv_result in res_json[0]["interval"]["intervalResults"]:
                res_count += 1
                # print(iv_result)
                ath_name = iv_result['displayName']
                ath_time_millis = iv_result['time']['timeInMillis']
                ath_time = convertMillis(ath_time_millis)
                if division is None:
                    # convert division
                    division_val = iv_result['gender']
                    if division_val == 'F':
                        division = "Female"
                    elif division_val == 'M':
                        division = 'Male'
                    else:
                        print("unknown division = ", division_val)

                cur.execute('''INSERT OR IGNORE INTO racedata (url, event, year, division,  place, athlete, time)
                        VALUES ( ?, ?, ?, ?, ?, ?, ? )''', ( url, event, year, division, res_count, ath_name, ath_time))

        print("\tresults extracted=", res_count)
    conn.commit()

    if res_count == 0:
        error_urls.append(url)

def convertMillis(millis):
    seconds=int((millis/1000)%60)
    minutes=int((millis/(1000*60))%60)
    hours=int((millis/(1000*60*60))%24)
    # print(f"{hours}:{minutes}:{seconds}")
    return(f"{hours}:{minutes}:{seconds}")


def main():
    # convertMillis(8611000)


    # fname = input("Enter file name: ")
    try:
        races_to_extract = int(input("enter number of urls to extract: "))
    except:
        print("error getting number of races")
        quit()

    try:
        fh = open(url_filename, 'r')
    except:
        print("cannot open file")
        quit()

    # file must be good to get here
    race_count = 0
    for url in fh:
        # check if the event has already been scanned
        #
        cur.execute('''select distinct url from racedata where url = ?''', ( url.strip(), ))
        try:
            row = cur.fetchone()
            if row is not None:
                # existing - skip it
                print(f"already scanned: {url}")
                continue
        except:
            pass

        race_count += 1


        if race_count > races_to_extract:
            print("ending,", race_count, "races already read")
            break
            # do ti
        url = url.rstrip()
        print("\nreading race", race_count, url)
        page_data, event, course,  division = get_page_content(url)
        if page_data is not None:
            parse_athlinks_page(url, page_data, event, course, division)

    print("urls with errors,", len(error_urls))
    print(error_urls)

    print("events added", race_count)
    # # process a url (hard coded to start with)
    # page_data, division = get_page_content("https://www.athlinks.com/event/20238/results/Event/795920/Course/1575400/Division/21686718/Results")
    # if page_data is not None:
    #     # parse the athlinks page
    #     parse_athlinks_page(page_data, division)
    #     # parse_athlinks_page('https://www.athlinks.com/event/20238/results/Event/795920/Course/1575400/Division/21686729/Results')

    # print("888888")
    # page_data, division = get_page_content('https://www.athlinks.com/event/20238/results/Event/795920/Course/1575400/Division/21686729/Results')
    # if page_data is not None:
    #     # parse the athlinks page
    #     parse_athlinks_page(page_data, division)

    # page_data, division = get_page_content('https://www.athlinks.com/event/6568/results/Event/888682/Course/1714699/Division/23324955/Results')
    # parse_athlinks_page(page_data, division)

if __name__ == '__main__':
    main()