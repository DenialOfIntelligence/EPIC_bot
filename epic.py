from time import sleep
import requests
import json
from os import system
import datetime
# Run at 08:30 and post the first image at 09:00 in !utc!
# then post the next one half an hour later
nasa_api_url = "https://epic.gsfc.nasa.gov/api/natural/"
mastodon_api_url = "https://botsin.space"
upload_url = f"{mastodon_api_url}/api/v2/media"
status_url = f"{mastodon_api_url}/api/v1/statuses"
access_token = ""  # Mastodon token
failed = False
counter = 1
id_file = open("last_id.txt", "r")
last_id = int(id_file.readline().strip('\n'))
id_file.close()

response = requests.get(nasa_api_url)
data = response.json()
id_new = int(data[0].get("identifier"))
if not last_id == id_new:
	last_id = id_new
	utc_time = datetime.datetime.now(tz=datetime.timezone.utc)
	for data in data:
		date = data.get("date")[:-9].split("-")
		date_human = data.get("date")[:-9]
		time = data.get("date")[-8:]
		image = data.get("image")+".png"
		wget_string = f"wget https://epic.gsfc.nasa.gov/archive/natural/{date[0]}/{date[1]}/{date[2]}/png/{image} -q "
		system(wget_string)
		print("image downloaded")

		# media uploading
		headers = {"Authorization": f"Bearer {access_token}"}
		with open(image, "rb") as image_file:
			try:
				image_response = requests.post(upload_url, headers=headers, files={"file": image_file})
			except requests.exceptions.RequestException as e:
				print(f"Error uploading Mastodon image: {e}")
				failed = True
			else:
				media_id = image_response.json()["id"]

		# Toting the cool image
		if not failed:
			mastodon_text = f"A new image from NASA's EPIC camera onboard the NOAA DSCOVR spacecraft made on {date_human} at {time}."
			post_time = utc_time + datetime.timedelta(minutes=30*counter)
			post_time = post_time.isoformat()
			toot_data = {
				"status": mastodon_text,
				"media_ids[]": media_id,
				"scheduled_at": post_time
				}
			try:
				toot_response = requests.post(status_url, headers=headers, data=toot_data)
			except requests.exceptions.RequestException as e:
				print(f"Error posting: {e}")
			else:
				# id_file = open("last_id.txt", "w")
				# id_file.write(f"{last_id}\n")
				# id_file.close()
				system(f"rm {image}")
				counter = counter + 1
