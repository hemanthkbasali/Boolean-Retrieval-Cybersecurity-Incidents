"""Boolean retrieval for cybersecurity incident reports.

Steps (same as the IR architecture taught in Module 1):
  documents -> tokenize -> inverted index -> Boolean query -> set operations -> results
"""
import csv
import os
import re

CSV_PATH = os.path.join(os.path.dirname(__file__), "incidents.csv")

STOPWORDS = {
    "a", "an", "the", "of", "in", "on", "to", "and", "or", "for", "by", "with",
    "is", "was", "were", "are", "as", "at", "it", "its", "that", "this", "from",
    "into", "so", "after", "before", "who", "all", "not",
}


PUNCTUATION = ".,;:!?()[]{}\"'"
MAX_QUERY_LENGTH = 200


def load_documents(path=CSV_PATH):
    """Read the CSV file and return {doc_id: row}."""
    docs = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            docs[int(row["id"])] = row
    return docs


def tokenize(text):
    """Lowercase, keep only letters, drop stopwords."""
    words = re.findall(r"[a-z]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def build_index(docs):
    """Inverted index: term -> set of ids of documents containing the term."""
    index = {}
    for doc_id, row in docs.items():
        text = row["title"] + " " + row["type"] + " " + row["description"]
        for term in tokenize(text):
            index.setdefault(term, set()).add(doc_id)
    return index


def parse_query(query):
    """Split a query into OR-groups of AND-terms.

    "malware AND NOT ransomware OR ddos"
      -> [[("malware", False), ("ransomware", True)], [("ddos", False)]]
    (term, True) means the term is negated with NOT.
    Precedence: NOT first, then AND, then OR. No brackets.
    """
    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError("Query is too long. Use at most " + str(MAX_QUERY_LENGTH) + " characters.")
    words = query.split()
    if not words:
        raise ValueError("Query is empty.")

    groups = [[]]          # list of OR-groups, each a list of (term, negated)
    negate = False
    expect_term = True     # True when the next word must be a term or NOT

    for word in words:
        upper = word.upper()
        if upper == "NOT":
            if not expect_term or negate:
                raise ValueError("NOT must come before a term, e.g. A AND NOT B.")
            negate = True
        elif upper in ("AND", "OR"):
            if expect_term:
                raise ValueError("Operator " + upper + " needs a term before it.")
            if upper == "OR":
                groups.append([])
            expect_term = True
        else:
            if not expect_term:
                raise ValueError("Put AND / OR between terms: '" + word + "'.")
            term = word.lower().strip(PUNCTUATION)   # "Malware," -> "malware"
            if not term:
                raise ValueError("'" + word + "' is not a search term.")
            if not re.fullmatch("[a-z]+", term):
                raise ValueError("'" + word + "' must contain letters only. For two words write A AND B, e.g. sql AND injection.")
            if term in STOPWORDS:
                raise ValueError("'" + term + "' is a common word that is not indexed. Remove it.")
            groups[-1].append((term, negate))
            negate = False
            expect_term = False

    if expect_term:
        raise ValueError("Query cannot end with an operator.")
    return groups


def search(query, index, all_ids):
    """Evaluate a Boolean query.

    Returns (sorted result ids, steps). Each step is (operator, text, ids):
    the operation that was done and the documents that remain after it.
    """
    groups = parse_query(query)
    steps = []
    result = set()
    for group in groups:
        group_set = None
        for term, negated in group:
            postings = index.get(term, set())
            steps.append(("LOOKUP", "Look up '" + term + "' in the index", sorted(postings)))
            if negated:
                postings = all_ids - postings
                steps.append(("NOT", "NOT " + term + ": every document except those", sorted(postings)))
            if group_set is None:
                group_set = postings
            else:
                group_set = group_set & postings              # AND = intersection
                steps.append(("AND", "AND: keep documents in both sets", sorted(group_set)))
        result = result | group_set                           # OR = union
        if len(groups) > 1:
            steps.append(("OR", "OR: join the sets so far", sorted(result)))
    return sorted(result), steps
