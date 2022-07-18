<div align="center" markdown>

<img src="https://i.imgur.com/MwQqR5r.png"/>

# Import images from Google Cloud Storage

<p align="center">

  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#Preparations">Preparations</a> •
  <a href="#How-To-Use">How To Use</a> •
  <a href="#History-Of-Runs">History of runs</a>
</p>

[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-from-google-cloud-storage)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/import-from-google-cloud-storage)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/import-from-google-cloud-storage)](https://supervise.ly)

</div>

## Overview

Application uploads images using links from provided CSV file. All images will be uploaded to single dataset. User chooses destination: workspace/project/dataset.  In addition, other columns can be attached to images as metainformation. 

<img src="https://i.imgur.com/YnaA9zA.png"/>

## How To Run

### Step 1. Add app from ecosystem

### Step 2: Run from context menu of project

Go to `Apps` page and press `Run` button in fron of the app.

<img src="https://i.imgur.com/2HciaQv.png"/>

## Preparations

### Step 1. Prepare CSV file with links
⚠️ **Important**: Column names have to be presented in the file. It is a hard requirement.  

### Step 2. Prepare JSON credentials file

Follow [these steps](https://cloud.google.com/docs/authentication/getting-started) to download JSON-file with credentials for Google Cloud Storage. Be sure, that you have permissions to work via API with the data in bucket. If permissions are incorrect, you may see errors like this:

```
max-***@***-***.iam.gserviceaccount.com does not have storage.objects.get access 
to the Google Cloud Storage object.: ('Request failed with status code', 403, ...)
```

### Step 3. Upload CSV and JSON files to your team

Upload two files from previous step to the Files in your team. There are no restrictions on file names. Files can be placed to any location in your team.

<img src="https://i.imgur.com/XNCEIJj.png"/>

## How To Use

Application has 5 cards. User has to go through all these cards (steps). Let's take a look at every step.

### Step 1. Provide path to CSV file

In `Files` right-mouse click context menu will help you to get the full path to file and copy it to buffer. 

<img src="https://i.imgur.com/VuBOyH7.png" height="400"/>

Paster it here

<img src="https://i.imgur.com/b5CUCZH.png"/>

And press `Preview` button. First five rows from your CSV file will pe presented. 

<img src="https://i.imgur.com/UIxbL8s.png"/>

### Step 2. Set Up CSV columns

<img src="https://i.imgur.com/MDciSf1.png"/>

Define, what column stores URL and the action that is applied to other columns:
- `ignore` - other columns are ignored
- `add to image as meta information` - other columns will be added to image as metainformation. User can view this information in labeling interface under the tab `Data` in images list.


### Step 3. URL modification (optional)

Every object in Google Cloud Storage has two types of links to objects (files): URI and URL.  

<img src="https://i.imgur.com/GmWXfki.png"/>

To better understand these links, let's consider simple example. If your links starts with `gs://` (for example `gs://a/b/ccc-ddd.jpg`) they can not be directly use download images. So the `gs://` prefix will be replaced to `https://storage.cloud.google.com/` automatically by default. 

Also sometimes developers forget to add bucket name to the beginning of the link. So you can ask app to change `gs://` prefix to `https://storage.cloud.google.com/<you bucket name here>/`.

To run this modification just define original prefix and new prefix and press `Transform and Preview` button. First 5 rows from CSV will be 

### Step 4. Provide path to Google Cloud Storage Credentials

This step is similar to **Step 1** but for credentials JSON file. Insert path and press `Validate credentials on random URL`. Application will try to use your creds to download image and visualize it. Or it will show the error message from Google Cloud API. 

<img src="https://i.imgur.com/wUf7Afd.png"/>

### Step 5. Choose destination, image preprocessing settings and start upload

<img src="https://i.imgur.com/LufV2mR.png"/>

Define destination workspace/project/dataset. All images will be imported to a single dataset. If you want to create several datasets, you have to split you CSV-links file to several and run this app multiple times with every CSV file as input. 

Application will create workspace or/and project or/and dataset if they don't exist. If dataset exists - it's ok, images will be added to it (`appent mode`).

## History of runs

To see history of runs go to `Apps` page, click to applications sessions. In front of every session you can see several buttons buttons. Press `View` or `Open` button to open application session (in `Read Only` mode - if the application is stopped or finished).

<img src="https://i.imgur.com/WwdUXe4.png"/>
