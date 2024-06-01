#!/bin/bash

cd care-sponsors-scraper || exit

python visa-sponsor-scraper.py
python CQC-scraper.py

python prep-sponsors-data.py
python get-care-sponsors.py all
python get-care-sponsors.py current
python add-sponsors-group.py
python find-missing-sponsors.py

cd ..

cp care-sponsors-scraper/data-out/all-skilled-home-care-sponsors.csv data-preprocessor/data_preprocessor/store/data/all-skilled-home-care-sponsors.csv
cp care-sponsors-scraper/data-out/current-skilled-home-care-sponsors.csv data-preprocessor/data_preprocessor/store/data/current-skilled-home-care-sponsors.csv

. ./API_KEY

conda run -n data-preprocessor python -m data_preprocessor.create_location_lookup

cp data-preprocessor/data_preprocessor/store/output/current-skilled-home-care-sponsors-with-loc.csv care-sponsors-svelte-app/static/sponsors.csv
cp data-preprocessor/data_preprocessor/store/output/place_merc_lookup.json care-sponsors-svelte-app/static/place_merc_lookup.json