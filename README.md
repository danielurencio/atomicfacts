# forexSerie.py

Running ´getAllPairs()´ will download and store, in a MongoDB instance, hourly data for many pairs.

# fundamentals.py

Running ´getAllIds()´ will generate and download a JSON file with all series of a country related to fundamental indicators.

Within ´getAllIds´ a function named 'getBimesterCalendar' is executed. At the time, only one country is supported (US as specified by the id 5). This should be changed so that the country ID is passed as a parameter so that many series for multiple countries can be extracted.

A function that extracts all possible country IDs is yet to be added.

To download all available fundamentals, do:

    >>> arr = json.loads(open('ids.json').read())
    >>> downloadSeries(arr,'US')
