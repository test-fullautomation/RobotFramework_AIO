#!/usr/bin/env python3
"""
Parst eine Bazel Build Event Protocol (BEP) JSON-Datei
(erzeugt mit --build_event_json_file=bep.json) und extrahiert
Testergebnisse (TestResult / TestSummary Events).

Aufruf:
    python3 parse_bep.py bep.json
    python3 parse_bep.py bep.json --only-failed
    python3 parse_bep.py bep.json --format csv > results.csv
"""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict


def iter_events(path):
    """Liest die BEP-Datei zeilenweise (NDJSON: ein JSON-Objekt pro Zeile)."""
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"Warnung: Zeile {lineno} ist kein gueltiges JSON ({exc})",
                      file=sys.stderr)


def label_from_id(event_id: dict, key: str) -> str:
    """Extrahiert das Target-Label aus einer BuildEventId-Struktur."""
    sub = event_id.get(key, {})
    return sub.get("label", "unbekannt")


def extract_test_results(events):
    """Liefert eine Liste von Dicts, eine pro TestResult-Attempt."""
    results = []
    for event in events:
        test_result = event.get("testResult")
        if test_result is None:
            continue

        event_id = event.get("id", {})
        tr_id = event_id.get("testResult", {})

        outputs = [
            out.get("uri", "")
            for out in test_result.get("testActionOutput", [])
        ]

        results.append({
            "label": tr_id.get("label", "unbekannt"),
            "run": tr_id.get("run"),
            "shard": tr_id.get("shard"),
            "attempt": tr_id.get("attempt"),
            "status": test_result.get("status", "UNKNOWN"),
            "cached": test_result.get("cachedLocally", False),
            "duration_ms": test_result.get("testAttemptDurationMillis"),
            "outputs": outputs,
        })
    return results


def extract_test_summaries(events):
    """Liefert eine Liste von Dicts, eine pro Target (aggregiertes Ergebnis)."""
    summaries = []
    for event in events:
        test_summary = event.get("testSummary")
        if test_summary is None:
            continue

        event_id = event.get("id", {})
        ts_id = event_id.get("testSummary", {})

        summaries.append({
            "label": ts_id.get("label", "unbekannt"),
            "overall_status": test_summary.get("overallStatus", "UNKNOWN"),
            "total_run_count": test_summary.get("totalRunCount"),
            "total_num_cached": test_summary.get("totalNumCached"),
            "num_passed": len(test_summary.get("passed", [])),
            "num_failed": len(test_summary.get("failed", [])),
        })
    return summaries


def extract_junit_xml_paths(events):
    """Liefert eine Liste von Dicts mit Label, Attempt-Info und Pfad/URI
    aller JUnit-XML-Testergebnisse (Bazel benennt diese 'test.xml')."""
    rows = []
    for event in events:
        test_result = event.get("testResult")
        if test_result is None:
            continue

        event_id = event.get("id", {})
        tr_id = event_id.get("testResult", {})

        for out in test_result.get("testActionOutput", []):
            name = out.get("name", "")
            if name != "test.xml":
                continue
            uri = out.get("uri", "")
            rows.append({
                "label": tr_id.get("label", "unbekannt"),
                "run": tr_id.get("run"),
                "shard": tr_id.get("shard"),
                "attempt": tr_id.get("attempt"),
                "status": test_result.get("status", "UNKNOWN"),
                "name": name,
                "path": uri[len("file://"):] if uri.startswith("file://") else uri,
            })
    return rows


def print_table(rows, columns):
    if not rows:
        print("Keine Ergebnisse gefunden.")
        return
    widths = {c: max(len(c), max(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    header = "  ".join(c.ljust(widths[c]) for c in columns)
    print(header)
    print("-" * len(header))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))


def print_csv(rows, columns):
    writer = csv.DictWriter(sys.stdout, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)


def main():
    parser = argparse.ArgumentParser(description="Testergebnisse aus einer Bazel BEP-JSON-Datei extrahieren.")
    parser.add_argument("bep_file", help="Pfad zur BEP-JSON-Datei (--build_event_json_file)")
    parser.add_argument("--mode", choices=["summary", "attempts"], default="summary",
                         help="'summary' = aggregiert pro Target (Default), 'attempts' = jeder einzelne Testlauf")
    parser.add_argument("--only-failed", action="store_true",
                         help="Nur nicht-erfolgreiche Ergebnisse anzeigen")
    parser.add_argument("--format", choices=["table", "csv"], default="table",
                         help="Ausgabeformat (Default: table)")
    parser.add_argument("--label", help="Nur ein bestimmtes Target filtern, z.B. //foo:bar_test")
    parser.add_argument("--xml-only", action="store_true",
                         help="Nur Pfade/Namen der JUnit-XML-Testergebnisse (test.xml) ausgeben, "
                              "ignoriert --mode")
    args = parser.parse_args()

    events = list(iter_events(args.bep_file))

    if args.xml_only:
        rows = extract_junit_xml_paths(events)
        columns = ["label", "run", "shard", "attempt", "status", "name", "path"]
        if args.only_failed:
            rows = [r for r in rows if r["status"] != "PASSED"]
        if args.label:
            rows = [r for r in rows if r["label"] == args.label]

        if args.format == "csv":
            print_csv(rows, columns)
        else:
            print_table(rows, columns)
        return

    if args.mode == "attempts":
        rows = extract_test_results(events)
        columns = ["label", "run", "shard", "attempt", "status", "cached", "duration_ms"]
        if args.only_failed:
            rows = [r for r in rows if r["status"] != "PASSED"]
    else:
        rows = extract_test_summaries(events)
        columns = ["label", "overall_status", "total_run_count", "total_num_cached", "num_passed", "num_failed"]
        if args.only_failed:
            rows = [r for r in rows if r["overall_status"] != "PASSED"]

    if args.label:
        rows = [r for r in rows if r["label"] == args.label]

    if args.format == "csv":
        print_csv(rows, columns)
    else:
        print_table(rows, columns)

        # Kurze Zusammenfassung am Ende (nur im table-Modus, nicht bei --format csv)
        status_key = "status" if args.mode == "attempts" else "overall_status"
        counts = Counter(r[status_key] for r in rows)
        if counts:
            print()
            print("Zusammenfassung: " + ", ".join(f"{k}={v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
