import functools
import logging

from django.db import DatabaseError
from django.shortcuts import render
from django.views.decorators.http import require_safe

from .evaluation import TESTS, evaluate
from .models import Incident
from .search import build_index, parse_query, search

logger = logging.getLogger(__name__)

_cache = {}


class DataNotReady(Exception):
    """The database has no incidents yet."""


def get_data():
    """Read incidents from the database and build the inverted index once, on first use."""
    if not _cache:
        docs = {
            i.id: {"title": i.title, "type": i.type, "description": i.description}
            for i in Incident.objects.all()
        }
        if not docs:
            raise DataNotReady()
        _cache["docs"] = docs
        _cache["index"] = build_index(docs)
        _cache["all_ids"] = set(docs)
    return _cache["docs"], _cache["index"], _cache["all_ids"]


def safe_page(view):
    """Only allow GET, and show a friendly page instead of crashing if anything goes wrong."""
    @require_safe
    @functools.wraps(view)
    def wrapper(request):
        try:
            return view(request)
        except (DataNotReady, DatabaseError):
            logger.exception("Database is not ready")
            message = ("The incident database is not ready. Run "
                       "python manage.py migrate and then python manage.py load_incidents.")
            return render(request, "finder/error.html", {"message": message}, status=503)
        except Exception:
            logger.exception("Unexpected error")
            message = "Something went wrong while building this page. Please try again."
            return render(request, "finder/error.html", {"message": message}, status=500)
    return wrapper


@safe_page
def home(request):
    """Search page: run the Boolean query and show the matching incidents."""
    docs, index, all_ids = get_data()
    query = request.GET.get("q", "").strip()
    context = {
        "doc_count": len(docs),
        "term_count": len(index),
        "query": query,
        "test_count": len(TESTS),
    }
    context["type_total"] = len({d["type"] for d in docs.values()})

    # Incident types with how many reports each has (shown on the start page).
    counts = {}
    for d in docs.values():
        counts[d["type"]] = counts.get(d["type"], 0) + 1
    biggest = max(counts.values())
    context["types"] = [
        {
            "name": name,
            "count": n,
            "width": round(100 * n / biggest),
            "query": " AND ".join(name.split()),   # "sql injection" -> "sql AND injection"
        }
        for name, n in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    if query:
        try:
            ids, steps = search(query, index, all_ids)
        except ValueError as e:
            context["error"] = str(e)
        else:
            context["results"] = [dict(docs[i], id=i) for i in ids]
            context["steps"] = [
                {
                    "number": n,
                    "op": op,
                    "text": text,
                    "count": len(found),
                    "width": round(100 * len(found) / len(docs)),   # bar length = share of all incidents
                    "ids": found,
                }
                for n, (op, text, found) in enumerate(steps, 1)
            ]
            pairs = [pair for group in parse_query(query) for pair in group]
            # Searched words (not NOT-ed) get highlighted in the results.
            context["terms"] = sorted({term for term, negated in pairs if not negated})
            # Query words that are in no incident at all (helps explain empty results).
            context["unknown"] = sorted({term for term, _ in pairs if term not in index})
            context["searched"] = True

    return render(request, "finder/index.html", context)


@safe_page
def dataset(request):
    """Shows the whole document collection."""
    docs, index, all_ids = get_data()
    rows = [dict(docs[i], id=i) for i in sorted(docs)]
    return render(request, "finder/dataset.html", {"rows": rows, "type_count": len({d["type"] for d in docs.values()})})


@safe_page
def index_page(request):
    """Shows the inverted index: every term, how many documents contain it, and their ids."""
    docs, index, all_ids = get_data()
    terms = [(term, len(ids), sorted(ids)) for term, ids in sorted(index.items())]
    average = round(sum(count for _, count, _ in terms) / len(terms), 1)
    return render(request, "finder/terms.html", {
        "terms": terms,
        "doc_count": len(docs),
        "term_count": len(terms),
        "average": average,
    })


@safe_page
def evaluation(request):
    """Runs the prepared test queries and shows precision and recall."""
    docs, index, all_ids = get_data()
    rows, avg_p, avg_r = evaluate(index, all_ids)
    perfect = sum(1 for r in rows if r["precision"] == 1 and r["recall"] == 1)
    return render(request, "finder/evaluation.html", {
        "rows": rows, "avg_p": avg_p, "avg_r": avg_r, "perfect": perfect,
    })
