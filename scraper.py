import os
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# MSHP url sorted by date
url = "https://www.mshp.dps.missouri.gov/HP71/SortFirstAction?column=date"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

fg = FeedGenerator()
fg.id(url)
fg.title('Missouri MSHP Arrest Reports')
fg.description('Automated RSS stream parsing the latest 5-day highway patrol arrest logs.')
fg.link(href=url, rel='alternate')

# Find the main data table
table = soup.find('table')
if table:
    rows = table.find_all('tr')
    # Loop rows skipping the header
    for row in rows[1:]:
        cols = [td.text.strip() for td in row.find_all('td')]
        if len(cols) >= 4:
            name, age, arrest_date, charge = cols[0], cols[1], cols[2], cols[3]
            
            fe = fg.add_entry()
            fe.id(f"{name.replace(' ', '_')}_{arrest_date}")
            fe.title(f"Arrest: {name} (Age: {age})")
            fe.description(f"Date: {arrest_date} <br/> Charges: {charge}")
            fe.link(href=url)

# Save the RSS file to the root directory
fg.rss_file('missouri_arrests.xml', pretty=True)
print("RSS Feed updated successfully.")
