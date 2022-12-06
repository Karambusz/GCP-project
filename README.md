# Content
- [Description](#description)
- [Architekture](#architekture)

# Description
Project that help monitoring the weather in Krakow using https://openweathermap.org/api.

# Architekture
![Architecture](architecture/GCP.png)

- Cloud Function - fetchs data about weather using https://openweathermap.org/api, creates blob files and then uploads them to GCS bucket
- Cloud Scheduler - job to trigger this cloud function
- Cloud Storage - store blob files 