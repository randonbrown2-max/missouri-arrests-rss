import os
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

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
    for row in rows:
        cols = [td.text.strip() for td in row.find_all('td')]
        
        # Ensure row has 8 columns and ignore header rows
        if len(cols) >= 8 and not cols[1].startswith('Name'):
            details_text = cols[0]  # "View details for report..."
            name = cols[1]
            age = cols[2]
            city_state = cols[3]
            arrest_date = cols[4]
            arrest_time = cols[5]
            county = cols[6]
            troop = cols[7]
            
            fe = fg.add_entry()
            # Unique entry ID
            fe.id(f"{name.replace(' ', '_')}_{arrest_date}_{arrest_time}")
            fe.title(f"{name} (Age: {age})")
            fe.description(
                f"<strong>City/State:</strong> {city_state}<br/>"
                f"<strong>Date/Time:</strong> {arrest_date} {arrest_time}<br/>"
                f"<strong>County/Troop:</strong> {county} County (Troop {troop})"
            )
            fe.link(href=url)

# Save the RSS file
fg.rss_file('missouri_arrests.xml', pretty=True)
print("RSS Feed updated successfully.")
