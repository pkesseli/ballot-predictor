# Swiss popular ballot predictor

## Python

### Setup venv
It is recommended to use a [Virtual Environment](https://docs.python.org/3/tutorial/venv.html) using the following command:
```bash
python -m venv .
```

### Install dependencies
All required Python dependencies can be installed using:
```bash
python -m pip install -r requirements.txt
```

### Generate training resources
src/python/bp/data contains data collection logic to scrape training data in 
the form of past ballots from www.bk.admin.ch. This data is persisted in
src/python/bp/resources to avoid repeated downloads.

When the project is first configured, or when the data should be updated with
the most recent data from www.bk.admin.ch, the following command can be used:
```bash
cd src/python
python -m bp.data.collector
```

### Tests
To run the python tests, use:
```bash
python -m unittest discover -s src/python
```

To run the python tests with coverage information, use:
```bash
python -m coverage run --source src/python -m unittest discover -s src/python; python -m coverage report --fail-under 100
```
