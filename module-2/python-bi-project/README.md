# Project: Business Intelligence with Python

## Overview

The goal of this project is to apply the things that I had learned in the previous lessons in data visualizations with python and derive Business Intelligence insights. For this project, I chose some data sets and other sources of information and explore them using Python. 

---

## Technical Tools

The technical tools I used were:

* Python
* Mongo (import databases)
* Pandas (data frames for data exploration)
* Matplotlib (for plotting graphs)
* Folium (maps and heatmaps)
* Selenium (web scraping)
* Numpy (for arrays manipulation)


## Project details:
### Goal: decide where (geographical position) to start/found a startup.
#### Startup details (simulation of a startup we want to found):
* **Name**: Habits.AI
* **Web page**: www.habits.ai
* **Description:** B2B platform for well-being and productivity. Through artificial intelligence, gamification, and behavioral science, we build healthy cultures that increase your employees’ engagement, productivity, loyalty and health.
* **Category**: Digital Health, well-being, B2B, technology, artificial intelligence & machine learning.
* **Important details/questions about the place**:
    * Want to be close to other tech companies.
    * There should be an entrepreneur ecosystem around the city and country (venture capitals, coworkings, universities, etc.).
    * There are big companies around (potencial clients).
    * How many startups fails in the city/country?



## Steps

The steps that I followed through the proccess of achieving the project were the following:

* Define a simulated startup I want to found/start.
* First step: organize data about startups around the world that are registered in Crunchbase: (Dataset url: https://www.kaggle.com/arindam235/startup-investments-crunchbase). Filter the startups in categories that matters for my startup.
* Second step: include the latitud and longitud of each city in the previous step DataFrame (Database url: https://www.kaggle.com/dataset/f66386cd35268fd2ae9c7c03e6e4d93c9b1607265c1adef13f99a76e420be997/version/1). The goal is to show the heatmap of the world with the position of the startups.
* Third step: Organize the dataframe by NUMBER OF STARTUPS in each Country/City.
* Fourth step: Organize the dataframe by FUNDING TOTAL (USD) (mean) in each Country/City.
* Fifth step: Organize the dataframe by STATUS (operating or closed) in each Country/City.
* Sixth step: Merge all the DataFrames from the steps below. Get the final ranking of cities.
* CITY SELECTION: After the analysis, the best city option to start Habits.AI (startup) will be Cambridge in USA.
* Seventh step: Map and analysis of Cambrige city. Make a map of the city that includes location of Venture Capitals, Universities, Coworking Spaces and Subway Stations. (Data scraped from Google Maps).
* Eighth step: Make a heatmap of Cambrige (with all the previous information) and take a decisition where to put the office.
* Final decision: As we can see on the map and heatmap, the best place to get an office and start Habits.AI, is around Kendall Square, there are three coworkings, it is close to more than 8 venture capital offices, have to access to public transportation and is few blocks away from the MIT University. The coworkings that are good option to have an office are The Link (www.link-kendall.org), Cambridge Coworking (www.cambridgecoworking.com) and Cove (www.cove.is).


## Next Steps:

* Get a more complete database about startups failures in cities/countries around the world to have a more confident analysis.
* Include a variable about living costs in the different cities.
* Include a variable about how easy (time and budget) is to start a company in each country.