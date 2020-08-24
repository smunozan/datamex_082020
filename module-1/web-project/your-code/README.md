# Project: API and Web Data Scraping

## Overview

The goal of this project is to practice diferent techniques to extract data (APIs and Web Scraping).

The steps that i did were:
* Choose a topic for the project. In my case I chose to work with information about cities and speciall details that you need when you want to plan a trip to one of those cities.
* Decide the columns that will show the result.
* Search for databases, APIs or webpages where you can get your data
* Start doing the queries and extracting the data from the different data sources.
* Get the final table and export it to CSV and JSON.

---

## Technical Details

The technical tools that I used for this project are as follows:

* API request using Python.
* Database (CSV) import to dataframesusing Pandas.
* Web Scraping using Beatutiful Soup
* Web Scraping using Selenium

## Data Sources

I used the following data sources:

1. First source: a public database of cities in the world (.csv) https://www.kaggle.com/dataset/f66386cd35268fd2ae9c7c03e6e4d93c9b1607265c1adef13f99a76e420be997/version/1
2. Second source: a public database of prices by city (web scrapping with Beautiful Soup)
https://www.numbeo.com/cost-of-living/prices_by_city.jsp?displayCurrency=USD&itemId=118&itemId=15&itemId=11&itemId=13&itemId=1
3. Third source: a public list of daily budget by city for backpackers (web scrapping with Beautiful Soup)
https://www.priceoftravel.com/world-cities-by-price-backpacker-index/
4. Fourth source: REST COUNTRIES API for getting countries information (currency name, language, region and subregion)
https://restcountries.eu/
5. Fifth source: 2 free APIs for exchange rate (fixer.io and exchangeratesapi.io)
https://fixer.io/documentation and https://exchangeratesapi.io/
6. Sixth source: Tripadvisor (web scrapping with Selenium)
https://www.tripadvisor.com/

## Important details

* Due to technichal details, the last source (Tripadvisor) was not completely implemented. Tripadvisor was working the same for every city, each city needed a special structure with Selenium so it was nos scalable.
* All the money values are in USD and the distances in KM.
* There were cities that have different names (small spelling changes) in each source so I used the library Fuzzuwuzzy to match the closest ones (After checking in detail, almost every city has the right match, but it is posible that a small percent has it wrong)

## Next steps

* Trying different techniques or getting a way to work with Tripadvisor (Maybe it can be with their API, but they say it is difficult to get the token if you are not an official webpage with thousends of users)
* Extracting data from other sources to complete the data of the cities that have anything incomplete.
