<div align="center">

# Boolean Retrieval for Cybersecurity Incidents

**Search incident reports with `AND`, `OR` and `NOT`, and see exactly how every answer was found.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-B3263A)

*Information Retrieval (BCY504B) &middot; CCA-1 Mini Project*

<br>

<img src="https://skillicons.dev/icons?i=python,django,sqlite,html,css,js,git,github&theme=dark" alt="Python, Django, SQLite, HTML, CSS, JavaScript, Git, GitHub">

</div>

## What is this?

A security team collects many incident reports. Reading them one by one is slow, and ordinary keyword search cannot say *"this word but not that one"*.

This project is a small search engine built on the **Boolean retrieval model**. You type words joined by `AND`, `OR` and `NOT`, and it returns exactly the reports that match. A **query trace** beside the results shows each step, so the answer is never a black box.

| Query | Meaning | Results |
|---|---|---|
| `ransomware AND hospital` | both words in the report | reports about hospital ransomware |
| `ddos OR botnet` | either word | 7 reports |
| `malware AND NOT ransomware` | malware, but not ransomware | 11 reports |

## How it works

```
Incident reports  ->  Tokenize  ->  Inverted index  ->  Query  ->  Set operations  ->  Results
```

1. **Tokenize.** Lowercase the text, keep letters only, drop stop words such as *the* and *is*.
2. **Inverted index.** A dictionary from each word to the set of documents that contain it, for example `ransomware -> {2, 9, 14, 20, 29, 31, 40, 46, 53}`.
3. **Parse the query.** Split it into words and operators. `NOT` binds first, then `AND`, then `OR`.
4. **Set operations.** Each operator is plain set maths:

| Operator | Set operation |
|---|---|
| `AND` | intersection |
| `OR` | union |
| `NOT` | all documents minus the word's set |

The retrieval logic is written by hand in [`finder/search.py`](finder/search.py). No search library is used.

## Features

- Boolean search with `AND`, `OR`, `NOT` and the precedence `NOT > AND > OR`
- **Query trace**: one row per set operation, with the number of incidents left after it
- Matched words highlighted in the results
- Dataset page and an **inverted index** page you can filter
- **Evaluation** page: precision and recall for 10 test queries against hand-judged answers
- Friendly messages for empty queries, misplaced operators, unknown words and over-long input
- Five colour themes, remembered in the browser

## Quick start

You need Python 3.10 or newer.

```bash
git clone https://github.com/hemanthkbasali/boolean-retrieval-cybersecurity-incidents.git
cd boolean-retrieval-cybersecurity-incidents

pip install -r requirements.txt
python manage.py migrate
python manage.py load_incidents
python manage.py runserver 8001
```

Open <http://localhost:8001/>.

To print the evaluation in the terminal instead:

```bash
python test_queries.py
```

## Dataset

60 synthetic cybersecurity incident reports written for this project (no real company data). Each has an id, a title, a type and a description, and lives in [`finder/incidents.csv`](finder/incidents.csv).

12 incident types: malware, ransomware, data breach, phishing, DDoS, insider threat, SQL injection, account takeover, social engineering, man-in-the-middle, XSS and DNS spoofing. The index holds 421 distinct terms built from the title, type and description.

## Evaluation

10 test queries, each compared with a relevant set judged by hand.

- **Precision** = relevant results returned / all results returned
- **Recall** = relevant results returned / all relevant documents

| Average precision | Average recall | Queries with both at 1.0 |
|---|---|---|
| **0.97** | **0.92** | 5 of 10 |

Where it falls short, and why:

- **Exact matching only.** Incident 12 says *stolen passwords*, so `breach AND credentials` misses it (recall 0.67).
- **Side mentions.** `insider OR employee` also returns reports where *employee* is only a detail (precision 0.67).
- **No ranking.** A document either matches or it does not.

## Project structure

```
manage.py
config/                       Django settings and root URLs
finder/
  search.py                   the IR core: tokenize, build_index, parse_query, search
  evaluation.py               10 test queries, precision and recall
  views.py                    request handling and page data
  models.py                   Incident table
  incidents.csv               the 60 reports
  management/commands/        load_incidents: CSV into SQLite
  templates/finder/           Search, Dataset, Inverted index, Evaluation pages
  static/finder/              style.css, script.js, self-hosted font
test_queries.py               prints the evaluation in the terminal
```

## Tech stack

<table>
  <tr>
    <td align="center" width="120"><img src="https://skillicons.dev/icons?i=python" width="48"><br><b>Python</b><br><sub>IR logic</sub></td>
    <td align="center" width="120"><img src="https://skillicons.dev/icons?i=django" width="48"><br><b>Django</b><br><sub>backend</sub></td>
    <td align="center" width="120"><img src="https://skillicons.dev/icons?i=sqlite" width="48"><br><b>SQLite</b><br><sub>database</sub></td>
    <td align="center" width="120"><img src="https://skillicons.dev/icons?i=html" width="48"><br><b>HTML</b><br><sub>pages</sub></td>
    <td align="center" width="120"><img src="https://skillicons.dev/icons?i=css" width="48"><br><b>CSS</b><br><sub>styling</sub></td>
    <td align="center" width="120"><img src="https://skillicons.dev/icons?i=js" width="48"><br><b>JavaScript</b><br><sub>small UI bits</sub></td>
  </tr>
</table>

Server-rendered pages, no JSON API, no search library.

## Ideas for later

- Stemming and synonyms to raise recall
- Ranked retrieval with TF-IDF or the vector space model
- A larger, real incident dataset

## Author

**Hemanth K Basali** &middot; 1DT24CY012
Dept. of CSE (Cyber Security), Dayananda Sagar Academy of Technology and Management

## License

[MIT](LICENSE)
