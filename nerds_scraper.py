import requests
import urllib
from bs4 import BeautifulSoup
import re

download_link_url = 'https://edunomicslab.org/nerds-download/'

response = requests.get(download_link_url)
html = response.text
soup = BeautifulSoup(html,'html.parser')

#content = soup.find(id="content")
content = soup.find(id="post-11226")
links = content.find_all('a', href=True)
#<div class="fusion-builder-row fusion-row fusion-flex-align-items-flex-start" 
for a in links:
	pattern = re.compile(".xlsx$")
	if pattern.search(a['href']):
		print("Scraping the URL:{url}".format(url=a['href']))
		response = requests.get(a['href'])
		#print(response)
		#print(response.content)
		filename_grab = re.search('https://edunomicslab.org/wp-content/uploads/.*/.*/(.*)', a['href'])
		if filename_grab:
			filename = filename_grab.group(1)
			file_path = "output/" + filename
			print(file_path)
			f = open(file_path, 'w')
			f.write(response.content)
			f.close()
	else:
		continue

