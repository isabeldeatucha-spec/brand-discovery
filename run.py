#!/usr/bin/env python3
"""
Sedge — AI Retail Broker Analyst

Commands
--------
try     Analyze a single brand-retailer pair from CLI args
batch   Analyze all pairs in a CSV file, save results to output/

Examples
--------
python run.py try \\
  --brand "Cove Soda" \\
  --category "prebiotic soda" \\
  --description "Clean prebiotic sparkling soda targeting health-conscious millennials. Strong DTC velocity." \\
  --retailer "Whole Foods" \\
  --retailer-type "natural channel"

python run.py batch --pairs pairs/sample.csv
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import anthropic

from src import config, analyzer

DECISION_COLORS = {"SEND": "\033[92m", "FLAG": "\033[93m", "SKIP": "\033[91m"}
RESET = "\033[0m"


def check_env():
    if not config.ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not set. Run: source ~/.zshrc")
        sys.exit(1)


def print_result(pair: dict, result: dict):
    decision = result["decision"]
    color = DECISION_COLORS.get(decision, "")
    print(f"\n{'─' * 60}")
    print(f"  {pair['brand']} → {pair['retailer']}")
    print(f"{'─' * 60}")
    print(f"  SCORE    : {result['score']}/100")
    print(f"  DECISION : {color}{decision}{RESET}")
    print(f"  RATIONALE: {result['rationale']}")

    if result.get("email"):
        print(f"\n  EMAIL DRAFT")
        print(f"  Subject  : {result['email']['subject']}")
        print(f"  Body     :\n")
        for line in result["email"]["body"].split("\n"):
            print(f"    {line}")


def save_result(pair: dict, result: dict, output_dir: Path):
    slug = f"{pair['brand'].lower().replace(' ', '_')}_{pair['retailer'].lower().replace(' ', '_')}"
    out = output_dir / f"{slug}.txt"
    lines = [
        f"{pair['brand']} → {pair['retailer']}",
        "─" * 60,
        f"SCORE    : {result['score']}/100",
        f"DECISION : {result['decision']}",
        f"RATIONALE: {result['rationale']}",
    ]
    if result.get("email"):
        lines += [
            "",
            "EMAIL DRAFT",
            f"Subject  : {result['email']['subject']}",
            "",
            result["email"]["body"],
        ]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def cmd_try(args):
    check_env()
    pair = {
        "brand": args.brand,
        "category": args.category,
        "description": args.description,
        "retailer": args.retailer,
        "retailer_type": args.retailer_type,
        "notes": args.notes,
    }
    print(f"Analyzing {args.brand} → {args.retailer}...")
    try:
        result = analyzer.analyze_pair(pair)
        print_result(pair, result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_batch(args):
    check_env()
    pairs_file = args.pairs
    if not Path(pairs_file).exists():
        print(f"Error: '{pairs_file}' not found.")
        sys.exit(1)

    with open(pairs_file, newline="", encoding="utf-8") as f:
        pairs = list(csv.DictReader(f))

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    print(f"Analyzing {len(pairs)} brand-retailer pairs...\n")
    results = []

    for i, pair in enumerate(pairs, 1):
        print(f"[{i}/{len(pairs)}] {pair['brand']} → {pair['retailer']}...", end=" ", flush=True)
        try:
            result = analyzer.analyze_pair(pair, client)
            path = save_result(pair, result, output_dir)
            print(f"{result['decision']} ({result['score']}/100) → {path.name}")
            results.append((pair, result))
        except Exception as e:
            print(f"ERROR: {e}")
        if i < len(pairs):
            time.sleep(1)

    # Summary
    print(f"\n{'─' * 60}")
    print(f"  SUMMARY")
    print(f"{'─' * 60}")
    for pair, result in sorted(results, key=lambda x: x[1]["score"], reverse=True):
        decision = result["decision"]
        color = DECISION_COLORS.get(decision, "")
        print(f"  {color}{decision}{RESET}  {result['score']:>3}/100  {pair['brand']} → {pair['retailer']}")

    sends = sum(1 for _, r in results if r["decision"] == "SEND")
    flags = sum(1 for _, r in results if r["decision"] == "FLAG")
    skips = sum(1 for _, r in results if r["decision"] == "SKIP")
    print(f"\n  {sends} SEND  {flags} FLAG  {skips} SKIP  |  output/ for full drafts")


def main():
    parser = argparse.ArgumentParser(prog="run.py", description="Sedge — AI Retail Broker Analyst")
    sub = parser.add_subparsers(dest="command", required=True)

    # try
    t = sub.add_parser("try", help="Analyze one brand-retailer pair")
    t.add_argument("--brand", required=True)
    t.add_argument("--category", required=True)
    t.add_argument("--description", required=True)
    t.add_argument("--retailer", required=True)
    t.add_argument("--retailer-type", default="", dest="retailer_type")
    t.add_argument("--notes", default="")

    # batch
    b = sub.add_parser("batch", help="Analyze all pairs in a CSV file")
    b.add_argument("--pairs", default="pairs/sample.csv", metavar="FILE")

    args = parser.parse_args()
    {"try": cmd_try, "batch": cmd_batch}[args.command](args)


if __name__ == "__main__":
    main()
