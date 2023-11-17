#!/bin/bash

SCORE_THRESHOLD=2
SYSTEM=m-nta
PREDICTIONS_DIR=data/names/m-nta/with_gpt-3.5
REFERENCES_DIR=data/names/gold
LOCALES=( ar de en es fr it ja ko ru zh )

for locale in ${LOCALES[@]}; do
    if [[ ! -f ${PREDICTIONS_DIR}/${locale}.${SYSTEM}.json ]]; then
        continue
    fi

    python src/evaluation/evaluate_coverage.py \
        --references_path ${REFERENCES_DIR}/${locale}.json \
        --predictions_path ${PREDICTIONS_DIR}/${locale}.${SYSTEM}.json \
        --score_threshold ${SCORE_THRESHOLD}
done