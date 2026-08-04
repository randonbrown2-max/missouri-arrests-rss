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
    "PHELPS",
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
        cols = [td.text.strip().replace('\xa0', ' ') for td in tds]
        
        # Must have at least 8 columns and avoid header rows
        if len(cols) >= 8 and not cols[1].lower().startswith('name'):
            # Normalize county string (remove extra spaces and force uppercase)
            raw_county = cols[6].strip().upper()
            
            # Check if any target county matches
            matched_county = next((c for c in TARGET_COUNTIES if c in raw_county), None)
            
            if matched_county:
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
                        clean_path = href if href.startswith('/') else f"/{href}"
                        report_link = f"https://www.mshp.dps.missouri.gov{clean_path}"

                fe = fg.add_entry()
                fe.id(f"{name.replace(' ', '_')}_{arrest_date}_{arrest_time}")
                fe.title(f"{name} (Age: {age})")
                fe.description(
                    f"<p><strong>City/State:</strong> {city_state}</p>"
                    f"<p><strong>Date/Time:</strong> {arrest_date} {arrest_time}</p>"
                    f"<p><strong>County/Troop:</strong> {raw_county} County (Troop {troop})</p>"
                )
                fe.link(href=report_link)

# Save the RSS file
fg.rss_file('missouri_arrests.xml', pretty=True)
print("RSS Feed updated successfully for Texas County area.")
