"""
evaluate_vanna.py — Benchmark Vanna AI's SQL generation accuracy.

This script:
  1. Loads a set of 30 test questions with gold-standard SQL
  2. Uses Vanna to generate SQL for each question
  3. Runs both gold and generated SQL against the database
  4. Compares results and scores accuracy
  5. Outputs a detailed report

Usage (from project root):
  cd backend
  python scripts/evaluate_vanna.py
"""

import json
import os
import sqlite3
import time
import traceback
from pathlib import Path

from dotenv import load_dotenv

# ── Path resolution ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "upi_transactions.db")
VECTOR_STORE_PATH = str(PROJECT_ROOT / "vector_store")

load_dotenv(PROJECT_ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Create a .env file in backend/ (see .env.example).")


# ── Initialize Vanna ─────────────────────────────────────────────────────────

from vanna.legacy.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.legacy.openai.openai_chat import OpenAI_Chat
from openai import OpenAI


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, client=None, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, client=client, config=config)


groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

vn = MyVanna(client=groq_client, config={
    "model": GROQ_MODEL,
    "path": VECTOR_STORE_PATH,
})
vn.connect_to_sqlite(DB_PATH)
print(f"[✓] Connected to {DB_PATH}\n")


# ── Test Benchmark ───────────────────────────────────────────────────────────

BENCHMARK = [
    # --- Basic Counts & Sums ---
    {
        "id": "T01",
        "question": "How many total transactions are there?",
        "gold_sql": "SELECT COUNT(*) as total FROM transactions",
        "category": "Basic",
    },
    {
        "id": "T02",
        "question": "What is the total amount of all successful transactions?",
        "gold_sql": "SELECT SUM(amount_inr) as total FROM transactions WHERE transaction_status = 'SUCCESS'",
        "category": "Basic",
    },
    {
        "id": "T03",
        "question": "How many distinct banks are there?",
        "gold_sql": "SELECT COUNT(DISTINCT sender_bank) as bank_count FROM transactions",
        "category": "Basic",
    },

    # --- Filtering ---
    {
        "id": "T04",
        "question": "How many transactions were made using iOS devices?",
        "gold_sql": "SELECT COUNT(*) as ios_count FROM transactions WHERE device_type = 'iOS'",
        "category": "Filtering",
    },
    {
        "id": "T05",
        "question": "What is the average amount of failed transactions?",
        "gold_sql": "SELECT AVG(amount_inr) as avg_failed FROM transactions WHERE transaction_status = 'FAILED'",
        "category": "Filtering",
    },
    {
        "id": "T06",
        "question": "How many fraud transactions happened on weekdays?",
        "gold_sql": "SELECT COUNT(*) as count FROM transactions WHERE fraud_flag = 1 AND is_weekend = 0",
        "category": "Filtering",
    },

    # --- GROUP BY ---
    {
        "id": "T07",
        "question": "How many transactions per device type?",
        "gold_sql": "SELECT device_type, COUNT(*) as count FROM transactions GROUP BY device_type",
        "category": "GroupBy",
    },
    {
        "id": "T08",
        "question": "What is the total transaction amount per bank?",
        "gold_sql": "SELECT sender_bank, SUM(amount_inr) as total FROM transactions GROUP BY sender_bank ORDER BY total DESC",
        "category": "GroupBy",
    },
    {
        "id": "T09",
        "question": "Show the number of transactions per transaction type.",
        "gold_sql": "SELECT transaction_type, COUNT(*) as count FROM transactions GROUP BY transaction_type",
        "category": "GroupBy",
    },

    # --- Date/Time ---
    {
        "id": "T10",
        "question": "How many transactions happened in March?",
        "gold_sql": "SELECT COUNT(*) as count FROM transactions WHERE strftime('%m', timestamp) = '03'",
        "category": "DateTime",
    },
    {
        "id": "T11",
        "question": "Show the total amount per month.",
        "gold_sql": "SELECT strftime('%Y-%m', timestamp) as month, SUM(amount_inr) as total FROM transactions GROUP BY month ORDER BY month",
        "category": "DateTime",
    },
    {
        "id": "T12",
        "question": "Which day of the week has the most transactions?",
        "gold_sql": "SELECT day_of_week, COUNT(*) as count FROM transactions GROUP BY day_of_week ORDER BY count DESC LIMIT 1",
        "category": "DateTime",
    },

    # --- CASE WHEN / Percentages ---
    {
        "id": "T13",
        "question": "What is the overall fraud rate?",
        "gold_sql": "SELECT (SUM(fraud_flag) * 100.0 / COUNT(*)) as fraud_rate FROM transactions",
        "category": "Percentage",
    },
    {
        "id": "T14",
        "question": "What is the success rate per network type?",
        "gold_sql": "SELECT network_type, (SUM(CASE WHEN transaction_status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate FROM transactions GROUP BY network_type",
        "category": "Percentage",
    },
    {
        "id": "T15",
        "question": "What percentage of transactions are P2P?",
        "gold_sql": "SELECT (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions)) as p2p_pct FROM transactions WHERE transaction_type = 'P2P'",
        "category": "Percentage",
    },

    # --- Multi-condition ---
    {
        "id": "T16",
        "question": "How many large successful P2P transactions are there?",
        "gold_sql": "SELECT COUNT(*) as count FROM transactions WHERE transaction_type = 'P2P' AND amount_tier = 'Large' AND transaction_status = 'SUCCESS'",
        "category": "MultiCondition",
    },
    {
        "id": "T17",
        "question": "Show failed Recharge transactions on WiFi.",
        "gold_sql": "SELECT transaction_id, amount_inr, sender_bank FROM transactions WHERE transaction_type = 'Recharge' AND transaction_status = 'FAILED' AND network_type = 'WiFi'",
        "category": "MultiCondition",
    },
    {
        "id": "T18",
        "question": "Average amount of fraud transactions from Karnataka on 4G?",
        "gold_sql": "SELECT AVG(amount_inr) as avg_amount FROM transactions WHERE fraud_flag = 1 AND sender_state = 'Karnataka' AND network_type = '4G'",
        "category": "MultiCondition",
    },

    # --- HAVING ---
    {
        "id": "T19",
        "question": "Which merchant categories have more than 5000 transactions?",
        "gold_sql": "SELECT merchant_category, COUNT(*) as count FROM transactions WHERE merchant_category IS NOT NULL GROUP BY merchant_category HAVING COUNT(*) > 5000",
        "category": "Having",
    },
    {
        "id": "T20",
        "question": "Which banks have a failure rate above 10%?",
        "gold_sql": "SELECT sender_bank, (SUM(CASE WHEN transaction_status = 'FAILED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as failure_rate FROM transactions GROUP BY sender_bank HAVING failure_rate > 10",
        "category": "Having",
    },

    # --- Cross-column ---
    {
        "id": "T21",
        "question": "What is the fraud rate per age group?",
        "gold_sql": "SELECT sender_age_label, (SUM(fraud_flag) * 100.0 / COUNT(*)) as fraud_rate FROM transactions GROUP BY sender_age_label",
        "category": "CrossColumn",
    },
    {
        "id": "T22",
        "question": "Show transaction count by state and transaction type.",
        "gold_sql": "SELECT sender_state, transaction_type, COUNT(*) as count FROM transactions GROUP BY sender_state, transaction_type ORDER BY sender_state, count DESC",
        "category": "CrossColumn",
    },

    # --- Ranking / TOP-N ---
    {
        "id": "T23",
        "question": "Which state has the most transactions?",
        "gold_sql": "SELECT sender_state, COUNT(*) as count FROM transactions GROUP BY sender_state ORDER BY count DESC LIMIT 1",
        "category": "Ranking",
    },
    {
        "id": "T24",
        "question": "Top 5 banks by average transaction amount.",
        "gold_sql": "SELECT sender_bank, AVG(amount_inr) as avg_amount FROM transactions GROUP BY sender_bank ORDER BY avg_amount DESC LIMIT 5",
        "category": "Ranking",
    },
    {
        "id": "T25",
        "question": "Show the 3 least common merchant categories.",
        "gold_sql": "SELECT merchant_category, COUNT(*) as count FROM transactions WHERE merchant_category IS NOT NULL GROUP BY merchant_category ORDER BY count ASC LIMIT 3",
        "category": "Ranking",
    },

    # --- NULL awareness ---
    {
        "id": "T26",
        "question": "Count transactions where merchant category is NULL.",
        "gold_sql": "SELECT COUNT(*) as null_count FROM transactions WHERE merchant_category IS NULL",
        "category": "NullHandling",
    },

    # --- Complex / Novel ---
    {
        "id": "T27",
        "question": "What is the average amount for each amount tier?",
        "gold_sql": "SELECT amount_tier, AVG(amount_inr) as avg_amount FROM transactions GROUP BY amount_tier",
        "category": "Novel",
    },
    {
        "id": "T28",
        "question": "How does the failure rate change by hour of day?",
        "gold_sql": "SELECT hour_of_day, (SUM(CASE WHEN transaction_status = 'FAILED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as failure_rate FROM transactions GROUP BY hour_of_day ORDER BY hour_of_day",
        "category": "Novel",
    },
    {
        "id": "T29",
        "question": "What is the ratio of P2P to P2M transactions?",
        "gold_sql": "SELECT (SELECT COUNT(*) FROM transactions WHERE transaction_type = 'P2P') * 1.0 / (SELECT COUNT(*) FROM transactions WHERE transaction_type = 'P2M') as p2p_to_p2m_ratio",
        "category": "Novel",
    },
    {
        "id": "T30",
        "question": "Show the overall transaction summary: total count, total amount, average amount, fraud count, and failure count.",
        "gold_sql": "SELECT COUNT(*) as total_txns, SUM(amount_inr) as total_amount, AVG(amount_inr) as avg_amount, SUM(fraud_flag) as fraud_count, SUM(CASE WHEN transaction_status = 'FAILED' THEN 1 ELSE 0 END) as failure_count FROM transactions",
        "category": "Novel",
    },
]


# ── Evaluation Engine ────────────────────────────────────────────────────────

def run_sql_safe(db_path: str, sql: str) -> list[dict] | None:
    """Execute SQL and return results as list of dicts, or None on error."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return result
    except Exception:
        return None


def results_match(gold_results: list[dict], gen_results: list[dict]) -> bool:
    """
    Compare two result sets. Returns True if they are functionally equivalent.
    We compare by checking if the same data is returned, regardless of column aliases.
    """
    if gold_results is None or gen_results is None:
        return False

    if len(gold_results) != len(gen_results):
        return False

    if len(gold_results) == 0:
        return True

    # Compare values only (ignore column name differences)
    gold_values = [tuple(row.values()) for row in gold_results]
    gen_values = [tuple(row.values()) for row in gen_results]

    # Try exact order match first
    if gold_values == gen_values:
        return True

    # Try sorted match (for unordered results)
    try:
        return sorted(gold_values) == sorted(gen_values)
    except TypeError:
        return False


def evaluate():
    """Run the full benchmark and produce a report."""

    print("=" * 70)
    print("  InsightX — Vanna AI Accuracy Benchmark")
    print(f"  Model: {GROQ_MODEL} | Tests: {len(BENCHMARK)}")
    print("=" * 70)
    print()

    results = []
    passed = 0
    failed = 0
    errors = 0
    category_stats = {}

    for i, test in enumerate(BENCHMARK):
        tid = test["id"]
        question = test["question"]
        gold_sql = test["gold_sql"]
        category = test["category"]

        print(f"[{tid}] {question}")

        # Generate SQL via Vanna (with rate-limit retry)
        gen_sql = None
        gen_error = None
        for attempt in range(3):
            try:
                gen_sql = vn.generate_sql(question)
                break
            except Exception as e:
                gen_error = str(e)
                if "429" in str(e) or "rate" in str(e).lower():
                    wait = 5 * (attempt + 1)
                    print(f"       ⏳ Rate limited, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    break

        if gen_sql is None:
            print(f"       ❌ FAILED — Could not generate SQL: {gen_error}")
            errors += 1
            results.append({**test, "status": "ERROR", "gen_sql": None, "error": gen_error})
            if category not in category_stats:
                category_stats[category] = {"pass": 0, "fail": 0, "error": 0}
            category_stats[category]["error"] += 1
            continue

        # Run both SQL queries
        gold_results = run_sql_safe(DB_PATH, gold_sql)
        gen_results = run_sql_safe(DB_PATH, gen_sql)

        # Compare
        match = results_match(gold_results, gen_results)

        if gen_results is None:
            status = "SQL_ERROR"
            print(f"       ❌ SQL_ERROR — Generated SQL failed to execute")
            print(f"       Generated: {gen_sql}")
            failed += 1
        elif match:
            status = "PASS"
            print(f"       ✅ PASS")
            passed += 1
        else:
            status = "FAIL"
            gold_count = len(gold_results) if gold_results else 0
            gen_count = len(gen_results) if gen_results else 0
            print(f"       ❌ FAIL — Results differ (gold: {gold_count} rows, gen: {gen_count} rows)")
            print(f"       Gold SQL: {gold_sql}")
            print(f"       Gen  SQL: {gen_sql}")
            failed += 1

        results.append({
            **test,
            "status": status,
            "gen_sql": gen_sql,
            "gold_rows": len(gold_results) if gold_results else 0,
            "gen_rows": len(gen_results) if gen_results else 0,
        })

        if category not in category_stats:
            category_stats[category] = {"pass": 0, "fail": 0, "error": 0}
        if status == "PASS":
            category_stats[category]["pass"] += 1
        elif status == "ERROR":
            category_stats[category]["error"] += 1
        else:
            category_stats[category]["fail"] += 1

        # Small delay to avoid rate limiting
        time.sleep(1)

    # ── Summary Report ───────────────────────────────────────────────────────
    total = len(BENCHMARK)
    accuracy = (passed / total * 100) if total > 0 else 0

    print("\n" + "=" * 70)
    print("  BENCHMARK RESULTS")
    print("=" * 70)
    print(f"  Total Tests:  {total}")
    print(f"  ✅ Passed:    {passed}")
    print(f"  ❌ Failed:    {failed}")
    print(f"  ⚠️  Errors:    {errors}")
    print(f"  📊 Accuracy:  {accuracy:.1f}%")
    print()

    print("  Category Breakdown:")
    print(f"  {'Category':<18} {'Pass':>6} {'Fail':>6} {'Error':>6} {'Acc%':>8}")
    print("  " + "-" * 46)
    for cat, stats in sorted(category_stats.items()):
        cat_total = stats["pass"] + stats["fail"] + stats["error"]
        cat_acc = (stats["pass"] / cat_total * 100) if cat_total > 0 else 0
        print(f"  {cat:<18} {stats['pass']:>6} {stats['fail']:>6} {stats['error']:>6} {cat_acc:>7.1f}%")
    print("=" * 70)

    # Save detailed results to JSON
    report_path = PROJECT_ROOT / "eval_report.json"
    report = {
        "model": GROQ_MODEL,
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "accuracy_pct": round(accuracy, 2),
        "category_stats": category_stats,
        "details": results,
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  📄 Detailed report saved to: {report_path}")

    return accuracy


if __name__ == "__main__":
    evaluate()
