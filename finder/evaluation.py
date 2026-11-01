"""Test queries with hand-judged relevant documents, and precision / recall."""
from .search import search

# query -> ids a human judged as relevant after reading all 60 reports
TESTS = [
    ("ransomware", {2, 9, 14, 20, 29, 31, 40, 46, 53}),
    ("phishing AND email", {1, 8, 24, 32, 52}),
    ("malware OR ransomware", {2, 5, 9, 11, 14, 17, 20, 23, 26, 29, 31, 32, 37, 40, 41, 42, 46, 47, 53, 55, 57}),
    ("malware AND NOT ransomware", {5, 11, 17, 23, 26, 32, 37, 41, 42, 47, 55, 57}),
    ("ddos OR botnet", {3, 10, 18, 33, 41, 48, 59}),
    ("breach AND credentials", {6, 12, 39}),
    ("credentials AND NOT phishing", {5, 6, 11, 12, 21, 28, 39, 49, 55, 56}),
    ("sql AND injection", {4, 19, 35, 50}),
    ("insider OR employee", {7, 16, 25, 36, 51, 60}),
    ("ransomware AND NOT hospital", {9, 14, 20, 29, 31, 40, 46, 53}),
]


def evaluate(index, all_ids):
    """Run every test query. Returns (rows, average precision, average recall)."""
    rows = []
    for query, relevant in TESTS:
        found, _ = search(query, index, all_ids)
        hits = set(found) & relevant
        precision = len(hits) / len(found) if found else 0
        recall = len(hits) / len(relevant)
        rows.append({
            "query": query,
            "retrieved": found,
            "relevant": sorted(relevant),
            "precision": round(precision, 2),
            "recall": round(recall, 2),
        })
    avg_p = round(sum(r["precision"] for r in rows) / len(rows), 2)
    avg_r = round(sum(r["recall"] for r in rows) / len(rows), 2)
    return rows, avg_p, avg_r
