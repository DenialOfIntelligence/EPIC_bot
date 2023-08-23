from time import sleep
import requests
import json
from os import system
nasa_api_url = "https://epic.gsfc.nasa.gov/api/natural/"
mastodon_api_url="https://botsin.space"
upload_url=f"{mastodon_api_url}/api/v2/media"
status_url = f"{mastodon_api_url}/api/v1/statuses"
access_token="" #Mastodon access token
id_file=open("last_id.txt","r")
last_id=int(id_file.readline().strip('\n'))
while True:
	response = requests.get(nasa_api_url)
	data = response.json()
	id_new=int(data[0].get("identifier"))
	if not last_id==id_new:
		date=data[0].get("date")[:-9].split("-")
		date_human=data[0].get("date")[:-9]
		time=data[0].get("date")[-8:]
		image=data[0].get("image")+".png"

		wget_string=f"wget https://epic.gsfc.nasa.gov/archive/natural/{date[0]}/{date[1]}/{date[2]}/png/{image} -q "
		system(wget_string)
		last_id=id_new
		id_file=open("last_id.txt","w")
		id_file.write(f"{last_id}\n")
		id_file.close()
		print("image downloaded")

		#media uploading
		headers = {"Authorization": f"Bearer {access_token}"}
		with open(image, "rb") as image_file:
			image_response = requests.post(upload_url, headers=headers, files={"file": image_file})
		media_id = image_response.json()["id"]

		#Toting the cool image
		mastodon_text=f"A new image from NASA's EPIC camera onboard the NOAA DSCOVR spacecraft made on {date_human} at {time}."
		toot_data = {
			"status": mastodon_text,
			"media_ids[]": media_id,
}
		toot_response = requests.post(status_url, headers=headers, data=toot_data)
	else:
		print("Image is is not new")
	sleep(600)
