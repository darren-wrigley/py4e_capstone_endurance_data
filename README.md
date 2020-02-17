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
use python & beautiful soup to extract the data from athlinks pages - will need to have a list of url's, as these are not predicable
- input - csv file with list of urls, with event, year, gender, url
