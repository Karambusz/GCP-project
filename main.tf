terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
    version = ">= 4.34.0"
    project = "serene-voltage-371417"
    region  = "us-central1"
    zone    = "us-central1-c"
}

resource "random_id" "bucket_prefix" {
  byte_length = 8
}

resource "google_storage_bucket" "bucket" {
  name                        = "${random_id.bucket_prefix.hex}-project-function-source"
  location                    = "US"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "project-bucket" {
  name                        = "project-gcp-weather-krakow"
  location                    = "US"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "object" {
  name   = "code.zip"
  bucket = google_storage_bucket.bucket.name
  source = "code.zip"
}

resource "google_storage_bucket_object" "redirect_object" {
  name   = "redirect.zip"
  bucket = google_storage_bucket.bucket.name
  source = "redirect.zip"
}

resource "google_cloudfunctions_function" "function" {
  name        = "get-weather-data"
  description = "fetchs data about weather creates blob files and then uploads them to GCS bucket"
  runtime     = "python37"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.object.name
  trigger_http          = true
  entry_point           = "weather"
}

resource "google_cloudfunctions_function" "redirect_function" {
  name        = "weather-krakow"
  description = "redirect to storage weather files by date and time"
  runtime     = "nodejs16"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.redirect_object.name
  trigger_http          = true
  entry_point           = "weatherInfo"
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

resource "google_cloudfunctions_function_iam_member" "redirect_invoker" {
  project        = google_cloudfunctions_function.redirect_function.project
  region         = google_cloudfunctions_function.redirect_function.region
  cloud_function = google_cloudfunctions_function.redirect_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

resource "google_cloud_scheduler_job" "project-gcp-weather-krakow-job" {
  name         = "weather-krakow-job"
  description  = "Get weather for Krakow every 15 minute"
  schedule     = "*/15 * * * *"
  http_target {
    http_method = "GET"
    uri = google_cloudfunctions_function.function.https_trigger_url
  }
}