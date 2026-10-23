# BANKING77 data provenance

## Source and scope

BANKING77 is a public English-language online-banking intent-classification benchmark released by PolyAI. The official CSV files contain text and category columns: 10,003 training rows, 3,080 test rows, and 77 intent labels. These counts were checked after download. This is a customer-service intent proxy, not an IT service-desk incident dataset.

- Official source: https://github.com/PolyAI-LDN/task-specific-datasets
- Dataset card: https://huggingface.co/datasets/PolyAI/banking77
- Primary paper: Casanueva et al. (2020), Efficient Intent Detection with Dual Sentence Encoders, https://arxiv.org/abs/2003.04807
- Pinned source commit: 57ec275d8078af65b7731c2a98be812d844a6d6b
- Retrieval: 2026-10-18T19:40:44.597257+00:00

## Origin and limitations

The paper describes customer-service queries but does not establish the collection method or whether all queries came from real customer interactions. The dataset card leaves initial collection and source-language producers unspecified. Accordingly, do not claim these are verified real production tickets, and do not label them as definitively synthetic either. Use the term public banking intent benchmark.

The source does not contain priority, urgency, timestamps, service-level agreements, resolution outcomes, agent replies, or quality-review scores. Any such fields added by this project are simulated metadata or explicit project-defined rules, not source ground truth. Results on this benchmark do not establish performance on workplace IT tickets or production business impact.

## License and attribution

The repository explicitly licenses its datasets under Creative Commons Attribution 4.0 International (CC BY 4.0). Redistribution and adaptation require appropriate attribution, a license link, and an indication of changes. Preserve LICENSE_CC_BY_4_0.txt with redistributed data; keep a separate code license if desired.

- Source license: https://github.com/PolyAI-LDN/task-specific-datasets/blob/57ec275d8078af65b7731c2a98be812d844a6d6b/LICENSE
- License: https://creativecommons.org/licenses/by/4.0/
- Suggested attribution: BANKING77 by PolyAI, described in Casanueva et al. (2020), Efficient Intent Detection with Dual Sentence Encoders. Source: https://github.com/PolyAI-LDN/task-specific-datasets. Licensed CC BY 4.0. Raw source files are unmodified; any processed files and project-added metadata are described separately.

## Reproducibility

All raw files below were downloaded successfully without an account or API key from the pinned official raw GitHub URLs. SOURCE_MANIFEST.json records exact URLs, byte counts, retrieval time and SHA-256 checksums.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| train.csv | 839073 | b06e26ac675513959a63135f11b94ea7786ed02da65db93a5650d8838cbc664b |
| test.csv | 239961 | d12d6e3bc4c3103966ae786dc435913c0c563dfa328f5a3646d0e62cfeeb474d |
| categories.json | 2036 | 53261da888122daf2d120d925458631d9619e15d82e56052e7a42e535ce32b63 |
| LICENSE_CC_BY_4_0.txt | 18650 | 7e7170e3cebf88a9f60c7b8421418323c09304da1af4d5e90f4da1dc1c8a2661 |
| SOURCE_README.md | 4735 | 7b9ce9069931cc2de89dce8c7ffb53d07806cf413601ccf133b9af5227b3a373 |

## Leakage check

A preliminary audit using lowercase text, stripped edges and collapsed whitespace found 4 repeated normalized texts within training, 1 within test, and 7 normalized text strings shared across the official splits. This is not a recommendation to tune on the test set. Document the chosen exact-deduplication policy, preserve original raw files, and derive validation only from the training split. The source test split has 40 rows per intent; training counts range from 35 to 187.
