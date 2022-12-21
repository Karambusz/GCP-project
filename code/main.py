from flask import jsonify
import requests
from google.cloud import storage
import json
from datetime import datetime
from datetime import date

storage_client = storage.Client(project='serene-voltage-371417')

def create_html_content(description, temperature, city, icon_url, dt_string):
	html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Current Weather</title>
  <link href="https://fonts.googleapis.com/css?family=Montserrat:400,900" rel="stylesheet">
  <style>
	body {{
    font-family: 'Montserrat', sans-serif;
    font-weight: 400;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    text-shadow: .1em .1em 0 rgba(0,0,0,0.3);
    font-size: 1.3em;
    height: 100vh;
    background-image: linear-gradient(to right top, #99bbcb, #a5c7d7, #b1d4e2, #bde0ee, #c9edfa);
}}
h1 {{
    margin: 0 auto;
    font-size: 2.2em;
    text-align: center;
    color: #fff;
    font-size: 5em;
}}
body.sunny {{
    background-image: linear-gradient(to right top, #ff4e50, #ff713e, #ff932b, #ffb41d, #f9d423);
}}
body.cloudy {{
    background-image: linear-gradient(to right top, #63747c, #71858e, #7f96a0, #8da8b2, #9bbac5);
}}
body.rainy {{
    background-image: linear-gradient(to right top, #637c7b, #718e8c, #7ea09e, #8db2b0, #9bc5c3);
}}

#description {{
	padding-top: 35px;
}}
  </style> 
</head>
<body>
	<div class="bg"></div>
	<div>
	<div style="display: flex;">
		<div id="description"><span>{description}</span></div>
		<div>
			<img src={icon_url} alt="weather">
		</div>
	</div>
    <h1 id="temp">{temperature} &#8451</h1>
    <div id="location">{city} {dt_string}</div>
  </div>
</body>
</html>	
	"""

	return html_content

def upload_blob(bucket_name, source_data, destination_blob_name):

    """Uploads a file to the bucket. """
    print('function upload_blob called')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(source_data, content_type='text/html')
    print('File {} uploaded to {}.'.format(
    destination_blob_name, bucket_name))

def list_blobs(bucket_name):
    """Lists all the blobs in the bucket. """
    blobs = storage_client.list_blobs(bucket_name)
    for blob in blobs:
        print(blob.name)

def weather(request):
    data = {"success": False}
    result = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q=Krakow,pl&APPID=aed39946f8ed261b8546978c0abce3f6&units=metric")
    data["response"] = result.json()
    data["success"] = True
    bucket_name = 'project-gcp-weather-krakow'
    local_data = json.dumps(data["response"])
    now = datetime.now()

    description = data["response"]["weather"][0]['main']
    temperature = data["response"]["main"]['temp']
    city = data["response"]["name"]
    icon_code = data["response"]["weather"][0]['icon']
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    
    dt_string = now.strftime("%d_%m_%Y_%H:%M")
    dt_string_without_time = now.strftime("%d.%m.%Y")

    html_content = create_html_content(description, temperature, city, icon_url, dt_string)

    file_name = str(dt_string)
    html_file_name = str(dt_string) + str('.html')

    upload_blob(bucket_name, local_data, dt_string_without_time + "/" + file_name)
    upload_blob(bucket_name, html_content, dt_string_without_time + "/" + html_file_name)
    print('Data inside of',bucket_name,':')
    return list_blobs(bucket_name)
