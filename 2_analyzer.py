import sqlite3

def get_seconds_for_time(time_string):
    time_parts = time_string.split(":")
    total_seconds = 0
    # must be 3 parts at the moment
    if len(time_parts) == 3:
        total_seconds = int(time_parts[0]) * 60 * 60
        total_seconds += int(time_parts[1]) * 60
        total_seconds += int(time_parts[2])
    else:
        print("invalid time to parse", time_string)

    print("seconds for time", time_string, total_seconds)
    return total_seconds


conn = sqlite3.connect('event_results.sqlite')
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS events ''')
cur.execute('''DROP TABLE IF EXISTS divisions ''')
cur.execute('''DROP TABLE IF EXISTS results ''')

# cur.execute('''CREATE TABLE IF NOT EXISTS events
    # (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE,
    #  athlinks_id INTEGER
    #  )''')
cur.execute('''CREATE TABLE IF NOT EXISTS events
    (id INTEGER PRIMARY KEY AUTOINCREMENT, name UNIQUE)''')

cur.execute('''CREATE TABLE IF NOT EXISTS athletes
    (id INTEGER PRIMARY KEY AUTOINCREMENT, name UNIQUE)''')

cur.execute('''CREATE TABLE IF NOT EXISTS results
    (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER, year INTEGER, division text, athlete_id, place integer, time_seconds integer)''')
# cur.execute('''CREATE TABLE IF NOT EXISTS Replies
#     (from_id INTEGER, to_id INTEGER)''')

# cache values
event_dict = dict()
athletes = dict()
# process each event result

con2 = sqlite3.connect('raw_racedata.sqlite')
cur2 = con2.cursor()

#cur2.execute("select * from racedata where event is not null limit 200")
cur2.execute("select * from racedata where event is not null")
for race_result in cur2 :
    division_url = race_result[1]
    event_name = race_result[2]
    year = int(race_result[3])
    division = race_result[4]
    print(event_name, year, division)
    place = int(race_result[5])
    athlete = race_result[6]
    finish_time = race_result[7]

    # division key create/lookup
    if event_name in event_dict.keys():
        # use cach ed value
        event_db_id = event_dict[event_name]
    else:
        # does the event exist in events
        cur.execute('INSERT OR IGNORE INTO events (name) VALUES ( ? )', ( event_name, ) )
        conn.commit()
        cur.execute('SELECT id FROM events WHERE name=? LIMIT 1', ( event_name, ))
        row = cur.fetchone()
        event_db_id = row[0]
        event_dict[event_name] = event_db_id
        print("fetched id from events db: ", event_db_id)


    # athlete
    if athlete in athletes.keys():
        # use cached value
        athlete_id = event_dict[event_name]
    else:
        # does the event exist in events
        cur.execute('INSERT OR IGNORE INTO athletes (name) VALUES ( ? )', ( athlete, ) )
        conn.commit()
        cur.execute('SELECT id FROM athletes WHERE name=? LIMIT 1', ( athlete, ))
        row = cur.fetchone()
        athlete_id = row[0]
        athletes[athlete] = athlete_id
        print("fetched athlete from athletes table: ", athlete_id)

    # calc time in seconds
    time_seconds = get_seconds_for_time(finish_time)
    cur.execute('''INSERT OR IGNORE INTO results (event_id, year, division, athlete_id,  place, time_seconds)
                   VALUES ( ?, ?, ?, ?, ?, ? )''',
                   ( event_db_id, year, division, athlete_id, place, time_seconds ) )
    conn.commit()


print("athletes = ", len(athletes))