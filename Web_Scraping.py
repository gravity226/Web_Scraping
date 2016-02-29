# Import library to read urls
from urllib2 import urlopen
# Import library to parse html
from bs4 import BeautifulSoup
import pandas as pd

# Go to the link and get the html as a string
content = urlopen('http://espn.go.com/college-football/bcs/_/year/2013').read()

# Feed the html to a BeatifulSoup object
soup = BeautifulSoup(content)

# Extract the rows in the table
odd_rows = soup.select('table tr.oddrow td')          #('table.mod-data tbody tr')
even_rows = soup.select('table tr.evenrow td')

# Extract the text in each cell and put into a list of list
# Such that each list in the list represents content in a row

l = []
count = 0
while count < len(odd_rows):
    if count == 0 or count % 18 == 0:
        l.append([ x.text for x in odd_rows[count : count+3] ])
        l.append([ x.text for x in even_rows[count : count+3] ])
    count += 1
'''
for row in rows:
    cell_lst = [cell for cell in row]
    table_lst.append(cell_lst)
'''
# print l

ranking = pd.DataFrame(l)
ranking.columns = ['ranking', 'state', 'score']

print ranking
