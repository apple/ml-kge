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


def read_references(input_path: str) -> Dict[str, List[str]]:
    data: Dict[int, List[str]] = {}

    with open(input_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            line_data = json.loads(line)
            wikidata_id = line_data["wikidata_id"]
            values = line_data["correct_values"]
            values = [normalize_value(v) for v in values]
            values = set(values)

            if values:
                data[wikidata_id] = values

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


def compute_micro_f1(
    precision_scores: List[List[float]],
    recall_scores: List[List[float]],
):
    precision_num = sum([sum(scores) for scores in precision_scores])
    precision_den = sum([len(scores) for scores in precision_scores])
    precision = precision_num / precision_den

    recall_num = sum([sum(scores) for scores in recall_scores])
    recall_den = sum([len(scores) for scores in recall_scores])
    recall = recall_num / recall_den

    f1 = 2 * precision * recall / (precision + recall)

    return precision, recall, f1


def compute_macro_f1(
    precision_scores: List[List[float]],
    recall_scores: List[List[float]],
):
    precision_scores = [sum(scores) / len(scores) for scores in precision_scores]
    recall_scores = [sum(scores) / len(scores) for scores in recall_scores]

    precision = sum(precision_scores) / len(precision_scores)
    recall = sum(recall_scores) / len(recall_scores)

    f1 = 2 * precision * recall / (precision + recall)

    return precision, recall, f1


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
    references = read_references(args.references_path)

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

    precision_scores = []
    recall_scores = []

    # Compute precision scores for all instances in the predictions.
    for id, instance_predictions in predictions.items():
        if args.wikidata_ids_path and id not in wikidata_ids:
            continue

        if id not in references:
            continue

        instance_references = references[id]
        instance_scores = []

        for prediction in instance_predictions:
            if prediction in instance_references:
                score = 1.0
            else:
                score = 0.0
            instance_scores.append(score)

        precision_scores.append(instance_scores)

        # If arg.print_pairwise_scores is set, print the scores for each entity.
        if args.print_pairwise_scores:
            print(id)
            print("    Gold:", instance_references)
            print("    Pred:", instance_predictions)
            _score = sum(instance_scores) / len(instance_scores)
            print(f"    Precision: {_score}")
            print()

    # Compute recall scores for all instances in the references.
    for id, instance_references in references.items():
        if args.wikidata_ids_path and id not in wikidata_ids:
            continue

        instance_predictions = predictions.get(id, [])

        instance_scores = []
        for reference in instance_references:
            if reference in instance_predictions:
                score = 1.0
            else:
                score = 0.0
            instance_scores.append(score)

        recall_scores.append(instance_scores)

        # If arg.print_pairwise_scores is set, print the scores for each entity.
        if args.print_pairwise_scores:
            print(id)
            print("    Gold:", instance_references)
            print("    Pred:", instance_predictions)
            _score = sum(instance_scores) / len(instance_scores)
            print(f"    Recall: {_score}")
            print()

    if not args.quiet:
        print(f"  # of entities in the references: {len(references):,}")
        print(f"  # of entities in the predictions: {len(predictions):,}")
        print("---------------------------")

    precision, recall, f1 = compute_micro_f1(precision_scores, recall_scores)

    if not args.quiet:
        print(f"  Coverage - P  = {100.*precision:0.1f}")
        print(f"  Coverage - R  = {100.*recall:0.1f}")
        print(f"  Coverage - F1 = {100.*f1:0.1f}")
        print("===========================")
        print()

    if args.quiet:
        print(f"{100.*precision:0.2f} {100.*recall:0.2f} {100.*f1:0.2f}")
