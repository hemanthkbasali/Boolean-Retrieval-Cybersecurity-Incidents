<div align="center">

# Boolean Retrieval for Cybersecurity Incidents

Search cybersecurity incident reports with `AND`, `OR` and `NOT`, and see how every answer was found.

<img src="https://skillicons.dev/icons?i=python,django,sqlite,html,css,js" alt="Python, Django, SQLite, HTML, CSS, JavaScript">

Information Retrieval (BCY504B) mini project

</div>

## What it does

You type a query like `malware AND NOT ransomware`. The app returns the matching incident reports and shows each step it took (the query trace).

- `AND` returns reports with both words (intersection)
- `OR` returns reports with either word (union)
- `NOT` returns reports without the word (everything except its set)

Words are cut into tokens, stored in an inverted index (word to the reports that contain it), and the operators work as set operations. The search code is in [`finder/search.py`](finder/search.py), written by hand with no search library.

## Run it

Needs Python 3.10 or newer.

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py load_incidents
python manage.py runserver 8001
```

Open http://localhost:8001/

## Pages

- **Search**: query box, results and query trace
- **Dataset**: the 60 incident reports
- **Inverted index**: every word and the reports that contain it
- **Evaluation**: precision and recall for 10 test queries (average 0.97 and 0.92)

## Files

```
finder/search.py        tokenize, inverted index, query parser, search
finder/evaluation.py    test queries, precision and recall
finder/views.py         pages
finder/incidents.csv    the 60 reports
test_queries.py         prints the evaluation in the terminal
```

## License

MIT
