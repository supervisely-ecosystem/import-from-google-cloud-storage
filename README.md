<div align="center" markdown>

<img src="https://i.imgur.com/MwQqR5r.png"/>

# Import images from Google Cloud Storage

<p align="center">

  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a> •
  <a href="#History-Of-Runs">History of runs</a>
</p>

[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-from-google-cloud-storage)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-from-google-cloud-storage&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-from-google-cloud-storage&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-from-google-cloud-storage&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

Application uploads images using links from provided CSV file. In addition, other columns can be attached to images as metainformation. 

## How To Run

### Step 0. Add app from ecosystem

### Step 1: Run from context menu of project

Go to `Apps` page and press `Run` button in fron of the app.

<img src="https://i.imgur.com/2HciaQv.png"/>

## How To Use

## History of runs

To see history of runs go to `Apps` page, click to applications sessions. In front of every session you can see several buttons buttons. Press `View` or `Open` button to open application session (in `Read Only` mode - if the application is stopped or finished).

<img src="https://i.imgur.com/WwdUXe4.png"/>


    # @TODO:  doc about bucket name in replace suffix
    #@TODO: readme error description: does not have storage.objects.get access to the Google Cloud Storage object.: ('Request failed with status code', 403, 'Expected one of', <HTTPStatus.OK: 200>, <HTTPStatus.PARTIAL_CONTENT: 206>)
    #@TODO: describe tasks destination in readme (что потом можно вохвращаться к сессиям и смотреть)
    #@TODO: расписать кейс дозагрузки
