# forexSerie.py

Running `getAllPairs()` will download and store, in a MongoDB instance, hourly data for many pairs.

# fundamentals.py

Running ```getAllIds()``` will generate and download a JSON file with the necessary information to obtaina country's fundamental time series. The obtained file is structured as an array of dictionaries that, when loaded as a variable, can be passed to other functions to do the _web scraping_.

Within `getAllIds` a function named `getBimesterCalendar` is executed. At the time, only one country is supported (US as specified by the id 5). This should be changed so that the country ID is passed as a parameter so that many series for multiple countries can be extracted.

__A function that extracts all possible country IDs is yet to be added.__

To download all available fundamentals, do:
```
    >>> arr = json.loads(open('ids.json').read())
    >>> downloadSeries(arr,'US')
```
