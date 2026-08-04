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
            # MSHP arrest table has at least 7 relevant columns
            if len(cols) >= 7:
                name = cols[0]
                age = cols[1]
                city_state = cols[2]
                arrest_date = cols[4]  # Column 4 is the actual Date
                arrest_time = cols[5]  # Column 5 is the Time
                charges = cols[6]      # Column 6 is Charges
                
                fe = fg.add_entry()
                fe.id(f"{name.replace(' ', '_')}_{arrest_date}")
                fe.title(f"{name} (Age: {age})")
                fe.description(f"<strong>Location:</strong> {city_state}<br/><strong>Date/Time:</strong> {arrest_date} {arrest_time}<br/><strong>Charges:</strong> {charges}")
                fe.link(href=url)

# Save the RSS file to the root directory
fg.rss_file('missouri_arrests.xml', pretty=True)
print("RSS Feed updated successfully.")
