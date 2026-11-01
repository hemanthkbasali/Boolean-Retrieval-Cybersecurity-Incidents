"""Prints the evaluation of the test queries (same numbers as the Evaluation page)."""
from finder.search import load_documents, build_index, search
from finder.evaluation import evaluate

docs = load_documents()
index = build_index(docs)
all_ids = set(docs)

print("Documents:", len(docs), "| Index terms:", len(index))
print()
rows, avg_p, avg_r = evaluate(index, all_ids)
for r in rows:
    print(f"Query: {r['query']}")
    print(f"  Retrieved: {r['retrieved']}")
    print(f"  Relevant : {r['relevant']}")
    print(f"  Precision={r['precision']:.2f}  Recall={r['recall']:.2f}")
print()
print(f"Average precision={avg_p:.2f}  Average recall={avg_r:.2f}")

print()
print("Edge cases")
for q in ["zebra", "NOT ransomware", "malware AND zebra", "AND malware", "malware ransomware", ""]:
    try:
        found, _ = search(q, index, all_ids)
        print(f"  '{q}' -> {len(found)} results {found[:8]}")
    except ValueError as e:
        print(f"  '{q}' -> error: {e}")
