# py4e_capstone_endurance_data
extract data related to mens/womens performance % differences in endurance events like boston marathon and ironman world championships

# the plan
extract 10-20 years of race results for some major endurance sporting events & compare winning & top bands (5/10/20) percentage peformance for men vs women.

# why?
i have read some articles saying that as the events get longer, women have a better capacity for endurance and the differences between the best women vs men should continue to get closer.

# how
using data from Athlinks (www.athlinks/.com) extract data for mens and womens top finishing times (~ 50 each - equal to the first page of results via athlinks)
- capture raw data - encluding event name, date (or just year?), gender, athlete name, finish time
  - create a simple data model to store the raw data
- create scripts to prepare data for analysis
  - winnning times - % difference for winning male/female - chart over time(years) to see if the difference is staying the same, or getting closer
  - top n times - e.g. does top 5/10/20 average times make a difference (may be an indicator of depth of field)

# techniques
use python & beautiful soup (https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to extract the data from athlinks pages - will need to have a list of url's, as these are not predicable
- input - csv file with list of urls, with event, year, gender, url

# events
start with Boston Marathon (https://www.baa.org/) - get the urls for the last 10-20 years for m/f fields - pro or non-pro, just get mens/womens finish times


# sql to group mens/womens results for each year (for first place)

## time diff for 1st place each year
basically we join the same table on itself, where the event/year/place are the same, filter each on the division (gender)
same could hold if we group-by bands and calculate an averate
Note:  percentage does not seem to work - cast as float?
```
select m.event_id, m.year, m.division, m.time_seconds,
       f.division, f.time_seconds,
       f.time_seconds - m.time_seconds as time_diff,
       (f.time_seconds - m.time_seconds) / m.time_seconds  as time_perc
from results m join results f on m.event_id = f.event_id and m.year = f.year and m.place = f.place
where m.place = 1 and m.division = 'Male' and f.division = 'Female'
order by time_diff asc;
```

## time diff for places 1 - 5 for each year

average time for places 1-5

```
select m.event_id, m.year, '1-5' as band, max(m.place),  avg(m.time_seconds) as male_time, avg(f.time_seconds) as female_time, avg(f.time_seconds - m.time_seconds) as time_diff, (f.time_seconds - m.time_seconds) / m.time_seconds  as time_perc
from results m join results f on m.event_id = f.event_id and m.year = f.year and m.place = f.place
where m.place >= 1 and m.place <=5 and m.division = 'Male' and f.division = 'Female'
group by m.event_id, m.year, band
order by time_diff asc;
```

adding bands for 1-10 and 10-20
```
select m.event_id, m.year, 'winner' as band, m.place, m.time_seconds as male_time, f.time_seconds as female_time, f.time_seconds - m.time_seconds as time_diff, (f.time_seconds - m.time_seconds) / m.time_seconds  as time_perc
from results m join results f on m.event_id = f.event_id and m.year = f.year and m.place = f.place
where m.place = 1 and m.division = 'Male' and f.division = 'Female'
union all
select m.event_id, m.year, '1-5' as band, max(m.place),  avg(m.time_seconds) as male_time, avg(f.time_seconds) as female_time, avg(f.time_seconds - m.time_seconds) as time_diff, (f.time_seconds - m.time_seconds) / m.time_seconds  as time_perc
from results m join results f on m.event_id = f.event_id and m.year = f.year and m.place = f.place
where m.place >= 1 and m.place <=5 and m.division = 'Male' and f.division = 'Female'
group by m.event_id, m.year, band
union all
select m.event_id, m.year, '1-10' as band, max(m.place),  avg(m.time_seconds) as male_time, avg(f.time_seconds) as female_time, avg(f.time_seconds - m.time_seconds) as time_diff, (f.time_seconds - m.time_seconds) / m.time_seconds  as time_perc
from results m join results f on m.event_id = f.event_id and m.year = f.year and m.place = f.place
where m.place >= 1 and m.place <=10 and m.division = 'Male' and f.division = 'Female'
group by m.event_id, m.year, band
union all
select m.event_id, m.year, '10-20' as band, max(m.place),  avg(m.time_seconds) as male_time, avg(f.time_seconds) as female_time, avg(f.time_seconds - m.time_seconds) as time_diff, (f.time_seconds - m.time_seconds) / m.time_seconds  as time_perc
from results m join results f on m.event_id = f.event_id and m.year = f.year and m.place = f.place
where m.place >= 10 and m.place <=20 and m.division = 'Male' and f.division = 'Female'
group by m.event_id, m.year, band
order by time_diff asc;


```

sqlite needs to use a printf to calculate a percentage - and cast as a real so it can be sorted properly
```
select m.event_id, m.year, 'winner' as band, m.place, m.time_seconds as male_time, f.time_seconds as female_time,
f.time_seconds - m.time_seconds as time_diff, cast(printf("%.2f",(printf("%.2f",f.time_seconds) - printf("%.2f",m.time_seconds)) / printf("%.2f",m.time_seconds) * 100) as real)  as time_perc
from results m join results f on m.event_id = f.event_id and m.year = f.year and m.place = f.place
where m.place = 1 and m.division = 'Male' and f.division = 'Female'
order by time_perc
```


Kona 2013 - results not available - adding manually

```
INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",1,"Frederik Van Lierde","8:12:29");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",2,"Luke McKenzie","8:15:19");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",3,"Sebastian Kienle","8:19:24");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",4,"James Cunnama","8:21:46");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",5,"Tim O'Donnell","8:22:25");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",6,"Ivan Rana","8:23:43");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",7,"Tyler Butterfield","8:24:09");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",8,"Bart Aernouts","8:25:38");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",9,"Timo Bracht","8:26:32");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Male",10,"Faris Al-Sultan","8:31:13");




INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",1,"Mirinda Carfrae","8:52:14");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",2,"Rachel Joyce","8:57:28");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",3,"Liz Blatchford","9:03:35");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",4,"Yvonne van Vlerken","9:04:34");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",5,"Caroline Steffen","9:09:09");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",6,"Caitlin Snow","9:10:12");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",7,"Meredith Kessler","9:10:19");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",8,"Michelle Vesterby","9:11:13");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",9,"Gina Crawford","9:14:47");

INSERT INTO "main"."racedata"("url","event","year","division","place","athlete","time")
VALUES (NULL, "Kona Ironman World Championship","2013","Female",10,"Linsey Corbin","9:17:22");



```


# ddl for anaysis table

```
CREATE TABLE "results_comp" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"event_id"	INTEGER NOT NULL,
	"year"	INTEGER NOT NULL,
	"band"	TEXT NOT NULL,
	"m_time_sec"	INTEGER NOT NULL,
	"f_time_sec"	INTEGER NOT NULL,
	"time_diff"	INTEGER NOT NULL,
	"percent_diff"	REAL NOT NULL
);
```

# create data for results_comp
```
insert into results_comp(event_id, year, band, m_time_sec, f_time_sec, time_diff, percent_diff)
select m.event_id,
	m.year,
	'winner' as band,
	m.time_seconds as m_time_sec,
	f.time_seconds as f_time_sec,
    f.time_seconds - m.time_seconds as time_diff,
	cast(printf("%.2f",(printf("%.2f",f.time_seconds) - printf("%.2f",m.time_seconds)) / printf("%.2f",m.time_seconds) * 100) as real)  as percent_diff
from
    results m join results f on m.event_id = f.event_id and m.year = f.year and m.place = f.place
where m.place = 1 and m.division = 'Male' and f.division = 'Female'
```