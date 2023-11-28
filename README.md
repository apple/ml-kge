# MKGE: Multilingual Knowledge Graph Enhancement

[**Task Description**](#task-description) |
[**WikiKGE-10**](#wikikge-10) |
[**Evaluation**](#evaluation) |
[**Paper**](https://arxiv.org/abs/2311.15781) |
[**Citation**](#citation) |
[**License**](#license)

Recent work in Natural Language Processing and Computer Vision has been leveraging textual information -- e.g., entity names and descriptions -- available in knowledge graphs to ground neural models to high-quality structured data.
However, when it comes to non-English languages, both quantity and quality of textual information are comparatively scarcer.
To address this issue, we introduce the task of automatic **Multilingual Knowledge Graph Enhancement (MKGE)** and perform a thorough investigation on bridging the gap in quantity and quality of textual information between English and non-English languages.
As part of our effort toward building better multilingual knowledge graphs, we also introduce **WikiKGE-10**, the first human-curated benchmark to evaluate MKGE approaches in 10 languages.
 
Please refer to our EMNLP 2023 paper for more details, [Increasing Coverage and Precision of Textual Information in Multilingual Knowledge Graphs](https://arxiv.org/abs/2311.15781).


## Task Description
The aim of MKGE is to evaluate automatic approaches in two subtasks:
* Increasing **coverage** of locale-specific facts in multilingual knowledge graphs;
* Increasing **precision** of locale-specific facts in multilingual knowledge graphs.

More specifically, we use *Wikidata* as our reference multilingual knoweldge graph, and we focus our study on *entity names*, which may or may not be represented in different ways across different languages.


### MKGE - Coverage
Suppose we want to add support to Wikidata for entity names (or other types of textual information, e.g., entity descriptions) in a new target language `l_t`.
*Coverage* measures the ability of an automatic approach to provide at least a valid entity name in `l_t` for each entity of interest in Wikidata.

In other words, measuring *Coverage* is equivalent to answering the following question: How effective is an automatic approach in converting the entity names from a source language `l_s` to a target language `l_t`?
For example, how can we use the English entity names to create valid Japanese entity names with the same quantity and quality of the English ones?

### MKGE - Precision
It is well-known that the quality of the information in Wikidata is not perfect.
*Precision* measures the ability of an automatic approach to identify incorrect entity names (or other types of textual information, e.g., entity descriptions) for an entity of interest in a target language `l_t`.

In other words, measuring *Precision* is equivalent to answering the following question: How effective is an automatic approach in recognizing noisy, incomplete, or outdated information in a target language `l_t`?


## WikiKGE-10
WikiKGE-10 is a benchmark for evaluating automatic approaches for increasing both **coverage** and **precision** of entity names in Wikidata for 10 languages.

WikiKGE-10 includes around 1000 entities in each of the following 10 languages:
* `ar` - Arabic
* `de` - German
* `en` - English
* `es` - Spanish
* `fr` - French
* `it` - Italian
* `ja` - Japanese
* `ko` - Korean
* `ru` - Russian
* `zh` - Simplified Chinese

### Dataset organization
The data is organized in the following way:
```
data
└── names
    ├── gold
    │   ├── ar.json
    │   ├── de.json
    ... ...
    ├── m-nta
    │   ├── with_gpt-3
    │   │   ├── ar.m-nta.json
    │   │   ├── de.m-nta.json
    ... ... ...
    │   ├── with_gpt-3.5
    │   │   ├── ar.m-nta.json
    │   │   ├── de.m-nta.json
    ... ... ...
    │   └── with_gpt-4
    │       ├── ar.m-nta.json
    │       ├── de.m-nta.json
    ... ... ...
    └── gpt
    │   ├── ar.gpt-3.json
    │   ├── de.gpt-3.json
    ... ...

    └── wikidata
        ├── ar.json
        ├── de.json
        ...
        └── zh.json
```
Where:
* `data/names/gold/` contains the human-curated data.
* `data/names/m-nta/` contains the predictions from M-NTA.
* `data/names/gpt/` contains the predictions from GPT-3 and GPT-3.5 (May 2023), and also GPT-4 (September 2023).
* `data/names/wikidata/` contains the data from Wikidata (May 2023).


### Human-curated data in WikiKGE-10
Here are a few examples in `data/names/gold/it.json`:
```json
{
    "wikidata_id": "Q48324",
    "correct_values": ["morale", "moralità", "Moralismo"],
    "incorrect_values": ["giudizio morale", "moralita'", "legge morale"]
}
```
```json
{
    "wikidata_id": "Q166844",
    "correct_values": ["Thomas N'Kono", "N'Kono"],
    "incorrect_values": ["Thomas Nkono"]
}

```

Where:
* `wikidata_id` is the QID of the entity in Wikidata.
* `correct_values` is a list of entity names that have been rated as valid by our human annotators.
* `incorrect_values` is a list of entity names that are in Wikidata but have been rated as invalid by our human annotators.


### M-NTA predictions in WikiKGE-10
We also include the entity names predicted by M-NTA, our automatic system for MKGE, to reproduces the results of our experiments.

Here are a few examples of the predictions found in `data/names/m-nta/no_gpt/it.json`:
```json
{
    "wikidata_id": "Q48324",
    "values": [
        [1, "Egenetica", false],
        [1, "Immorale", false],
        [1, "Immoralità", false],
        [1, "Morali", false],
        [1, "Moralismo", false],
        [1, "Moralità pubblica", false],
        [1, "Moralmente", false],
        [1, "Parenesi", false],
        [1, "Pubblica moralità", false],
        [1, "Regola morale", false],
        [1, "Teoria dei costumi", false],
        [4, "Morale", true],
        [4, "Moralità", true]
    ]
}
```
```json
{
    "wikidata_id": "Q166844",
    "values": [
        [1, "Thomas 'Tommy' N'Kono", false],
        [1, "Thomas Nucono", true],
        [1, "Tommy N'Kono", false],
        [3, "N'Kono", false],
        [3, "Nkono", false],
        [6, "Thomas N'Kono", true],
        [6, "Thomas NKono", false],
        [6, "Thomas Nkono", false]
    ]
}
```
Where:
* `wikidata_id` is the QID of the entity in Wikidata.
* `values` is a list of predictions from M-NTA:
    * `value[0]` is the confidence score from M-NTA
    * `value[1]` is the prediction from M-NTA
    * `value[2]` is whether the prediction comes from a Wikidata primary name.


## Evaluation
To evaluate the **coverage** of a system, you can run the following command:
```bash
python src/evaluation/evaluate_coverage.py \
    --references_path data/names/gold/es.json \
    --predictions_path data/names/m-nta/es.json \
    --score_threshold 2
```
You will see the following output:
```
===========================
Starting evaluation...
---------------------------
- Loading references from data/names/gold/es.json...
- Loading predictions from data/names/m-nta/with_gpt-3.5/es.m-nta.json...
  # of entities in the references: 1000
  # of entities in the predictions: 889
---------------------------
  Coverage - P  = 77.2
  Coverage - R  = 43.4
  Coverage - F1 = 55.6
===========================
```

To evaluate the **precision** of a system, you can run the following command:
```bash
python src/evaluation/evaluate_precision.py \
    --references_path data/names/gold/es.json \
    --predictions_path data/names/m-nta/es.json \
    --score_threshold 1
```
You will see the following output:
```
===========================
Starting evaluation...
---------------------------
- Loading references from data/names/gold/es.json...
- Loading predictions from data/names/m-nta/with_gpt-3.5/es.m-nta.json...
  # of entities: 1,000
  # of entities with correct names: 1,000
  # of entities with incorrect names: 1,000
  # of entities in the predictions: 951
---------------------------
  Total incorrect names: 571
  Identified incorrect names: 447
  Total correct names: 3,749
  Correct names classified as incorrect: 1,089
---------------------------
  Precision - P  = 71.9
  Precision - R  = 78.3
  Precision - F1 = 75.0
===========================
```

### Results
The main results from the paper can be found in `results/coverage` and `results/precision`.

## Citation
Please cite our work if you found WikiKGE-10, our [paper](), or these resources useful.

```bibtex
@inproceedings{conia-etal-2023-increasing,
    title = "Increasing Coverage and Precision of Textual Information in Multilingual Knowledge Graphs",
    author = "Conia, Simone  and
      Li, Min  and
      Lee, Daniel  and
      Minhas, Umar Farooq and
      Ilyas, Ihab and
      Li, Yunyao",
    booktitle = "Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP 2023)",
    month = dec,
    year = "2023",
    address = "Singapore",
    publisher = "Association for Computational Linguistics",
}
```

## License
The code in this repository is licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the [LICENSE.txt](LICENSE.txt) file.

WikiKGE-10 is licensed under [CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/deed.en), see the [LICENSE_Wikidata.txt](LICENSE_Wikidata.txt) file.

## Acknowledgements
This work is part of one of the projects I carried out during my internship at Apple.
I must truly thank Min Li and Yunyao Li for their incredible mentorship and for everything they taught me.
I would also like to thank Umar Farooq Minhas, Saloni Potdar, and Ihab Ilyas for their valuable feedback.
My gratitude also goes to Behrang Mohit for his insightful comments on the paper.
Besides his technical contributions, I would like to thank Daniel Lee for making this project more fun, and Farima Fatahi Bayat, Ronak Pradeep, and Revanth Gangi Reddy for making this internship a unique experience.
