# movies-popularity
Tool to store tweets about movies and preprocess them.

Movie date from: http://www.the-numbers.com/movies/release-schedule <br>
Converted to csv by: http://www.convertcsv.com/html-table-to-csv.htm

Before running:
```
pip install -r requirements.txt
python -m textblob.download_corpora
```

You also need rabbitmq to work with celery...
To process & get data:
```
./process.sh
```
