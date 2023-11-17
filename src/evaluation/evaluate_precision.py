#!/usr/bin/python3

"""Evaluate a set of translations against a set of references.

Reads the references contained in --references_path and the 
translations contained in --predictions_path and performs an
evaluation of the translation using a scorer specified by --scorer.

Typical usage example:

    python src/evaluation/evaluate_translations.py \
        --references_path references.json \
        --predictions_path predictions.json

"""

import argparse
import json
from typing import Dict, List


def normalize_value(value: str) -> str:
    value = value.lower()
    value = "".join([i for i in value if i.isalnum() or i == " "])
    return value


def read_file(input_path: str, field_name: str) -> Dict[str, List[str]]:
    data: Dict[int, List[str]] = {}

    with open(input_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            line_data = json.loads(line)
            if field_name in line_data:
                data[line_data["wikidata_id"]] = [
                    normalize_value(v) for v in line_data[field_name]
                ]

    return data


def read_predictions(input_path: str, threshold: int) -> Dict[str, List[str]]:
    data: Dict[int, List[str]] = {}

    with open(input_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            line_data = json.loads(line)
            wikidata_id = line_data["wikidata_id"]
            values = line_data["values"]
            values = [normalize_value(v) for s, v, *_ in values if s >= threshold]
            values = set(values)

            if values:
                data[wikidata_id] = values

    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--references_path",
        type=str,
        required=True,
        help="Path to the JSONL file containing the references.",
    )
    parser.add_argument(
        "--predictions_path",
        type=str,
        required=True,
        help="Path to the JSONL file containing the predictions.",
    )
    parser.add_argument(
        "--wikidata_ids_path",
        type=str,
        required=False,
        help="Allows the evaluation to be performed only on the subset of entities specified in this .txt file.",
    )
    parser.add_argument(
        "--print_pairwise_scores",
        action="store_true",
        help="If set, prints reference-prediction pairs.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Use this flag to reduce the verbosity of the output.",
    )
    parser.add_argument(
        "--score_threshold",
        type=int,
        default=0,
        help="Minimum score for the predictions to be evaluated.",
    )

    args = parser.parse_args()

    print("===========================")
    print("Starting evaluation...")
    print("---------------------------")

    # Load references.
    print(f"- Loading references from {args.references_path}...")
    references_correct = read_file(args.references_path, field_name="correct_values")
    references_incorrect = read_file(
        args.references_path, field_name="incorrect_values"
    )

    # Load predictions.
    print(f"- Loading predictions from {args.predictions_path}...")
    predictions = read_predictions(args.predictions_path, args.score_threshold)

    # Read Wikidata IDs if provided.
    if args.wikidata_ids_path:
        wikidata_ids = set()

        with open(args.wikidata_ids_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                wikidata_id = line.strip()
                wikidata_ids.add(wikidata_id)

    num_entities: int = 0
    num_incorrect_names: int = 0
    num_correct_names: int = 0
    num_true_incorrect: int = 0
    num_false_incorrect: int = 0

    all_ids = set(references_correct.keys())
    all_ids.update(set(references_incorrect.keys()))
    all_ids.update(set(predictions.keys()))

    for entity_id in sorted(all_ids):
        if args.wikidata_ids_path and entity_id not in wikidata_ids:
            continue

        num_entities += 1
        instance_predictions = predictions.get(entity_id, [])

        if entity_id in references_incorrect:
            incorrect_names = references_incorrect[entity_id]
            num_incorrect_names += len(incorrect_names)

            for incorrect_name in incorrect_names:
                if incorrect_name not in instance_predictions:
                    num_true_incorrect += 1

        if entity_id in references_correct:
            correct_names = references_correct[entity_id]
            num_correct_names += len(correct_names)

            for correct_name in correct_names:
                if correct_name not in instance_predictions:
                    num_false_incorrect += 1

    recall = num_true_incorrect / num_incorrect_names
    precision = (num_correct_names - num_false_incorrect + num_true_incorrect) / (
        num_correct_names + num_incorrect_names
    )
    f1 = 2 * precision * recall / (precision + recall)

    if not args.quiet:
        print(f"  # of entities: {len(all_ids):,}")
        print(f"  # of entities with correct names: {len(references_correct):,}")
        print(f"  # of entities with incorrect names: {len(references_incorrect):,}")
        print(f"  # of entities in the predictions: {len(predictions):,}")
        print("---------------------------")
        print(f"  Total incorrect names: {num_incorrect_names:,}")
        print(f"  Identified incorrect names: {num_true_incorrect:,}")
        print(f"  Total correct names: {num_correct_names:,}")
        print(f"  Correct names classified as incorrect: {num_false_incorrect:,}")
        print("---------------------------")
        print(f"  Precision - P  = {100 * precision:0.1f}")
        print(f"  Precision - R  = {100 * recall:0.1f}")
        print(f"  Precision - F1 = {100 * f1:0.1f}")
        print("===========================")
        print()

    if args.quiet:
        print(f"{100.*recall:0.1f} {100.*precision:0.1f} {100 * f1:0.1f}")
