from bs4 import BeautifulSoup
import csv

html = ""
with open("composio-servers.txt") as file:
    html = file.read()

soup = BeautifulSoup(html, 'html.parser')

cards = soup.find_all('a')
results = []

for card in cards:
    title_tag = card.find('h3')
    desc_tag = card.find('p')
    
    if title_tag and desc_tag:
        title = title_tag.get_text(strip=True)
        description = desc_tag.get_text(strip=True)
        results.append((title, description))

fieldnames = ['name', 'description']

with open("composio-servers.csv", 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for title, desc in results:
        print(f"Title: {title}\nDescription: {desc}\n")
        data = {"name": title, "description": desc}
        writer.writerow(data)
