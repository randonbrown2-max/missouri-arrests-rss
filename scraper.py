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
fg.title('Missouri MSHP Arrest Reports - Texas County Area')
fg.description('Automated RSS stream parsing arrest logs for Texas County, MO and surrounding counties.')
fg.link(href=url, rel='alternate')

# Texas County and bordering counties
TARGET_COUNTIES = {
    "TEXAS",
    "DENT",
    "SHANNON",
    "HOWELL",
    "DOUGLAS",
    "WRIGHT",
    "LACLEDE",
    "PULASKI"
}

# Find the main data table
table = soup.find('table')
if table:
    rows = table.find_all('tr')
    for row in rows:
        tds = row.find_all('td')
        cols = [td.text.strip() for td in tds]
        
        # Must have at least 8 columns and avoid header rows
        if len(cols) >= 8 and not cols[1].lower().startswith('name'):
            county = cols[6]
            
            # Filter for Texas County and surrounding area
            if county.upper() in TARGET_COUNTIES:
                name = cols[1]
                age = cols[2]
                city_state = cols[3]
                arrest_date = cols[4]
                arrest_time = cols[5]
                troop = cols[7]
                
                # Extract individual report detail URL if present
                report_link = url
                if tds[0].find('a') and tds[0].find('a').get('href'):
                    href = tds[0].find('a')['href']
                    if href.startswith('http'):
                        report_link = href
                    else:
                        report_link = f"https://www.mshp.dps.missouri.gov/HP71/{href.lstrip('/')}"

                fe = fg.add_entry()
                fe.id(f"{name.replace(' ', '_')}_{arrest_date}_{arrest_time}")
                fe.title(f"{name} (Age: {age})")
                fe.description(
                    f"<strong>City/State:</strong> {city_state}<br/><br/>"
                    f"<strong>Date/Time:</strong> {arrest_date} {arrest_time}<br/>"
                    f"<strong>County/Troop:</strong> {county} County (Troop {troop})"
                )
                fe.link(href=report_link)

# Save the RSS file
fg.rss_file('missouri_arrests.xml', pretty=True)
print("RSS Feed updated successfully for Texas County area.")
