# Public-release readiness review — November 4

**Not released.** Repository is still private; the current private upload includes forecasting, planner/UI, offline-tested Meta integration and these documents. See Git history for the exact upload commit. No deployment, visibility change, recording or submission has been performed.

## Required decisions / remaining blockers

- **Open-source license absent:** GitHub returns `licenseInfo: null`; no top-level project LICENSE exists. Owners need to approve the project license and confirm they can license all contributed code before release. The dataset's MIT notice does not license this application's code. This review does not make that decision for the owners.
- **Visibility approval:** the user authorized this private code upload. A private-to-public visibility change still requires separate authorization. Review the complete release diff, including whether the previously local launcher belongs in the release. Do not publish an older remote commit while demonstrating newer local features.
- **Personal paths/history:** Current README setup commands are portable. Earlier history may retain user-specific absolute paths; decide whether publishing that history is acceptable. Removing a string from the latest file does not remove historical copies. No history rewrite performed.
- **Meta:** synthetic-note extraction and human-confirmed session handoff are implemented and mock-tested, but there is no verified live response or durable audit. Mocked test results are not model evidence. Do not claim working Meta use or a complete Meta workflow. Account/model/budget access and authorized inference remain required before a real integration can be demonstrated.
- **Submission:** the provided event reminder requires a three-minute video and an open-source GitHub repository, with November 4 at 9 PM Eastern / 6 PM Pacific deadline. Rehearsal/recording, public release and final form completion remain user actions after these gates; no receipt exists.

## Completed scoped checks

- Common credential-pattern scan: **44 current candidate files**, **42 unique tracked historical blobs**, no matches. This is a scoped pattern check, not a guarantee of absence of every secret. It did not print or load ignored credential files.
- Ignore rules verified for `.env`, `.env.local`, virtual environment, raw dataset CSV, SQLite, evidence uploads and Streamlit secrets. Preserve these exclusions. Synthetic test fixtures are clearly labeled and contain no real customer data.
- Original fictional dataset provenance and gt MIT notice are retained in `data/PROVENANCE.md` and `data/raw/LICENSE-gt.txt`. Raw CSV is not committed; checksum-verified downloader remains reproducible. Rdatasets licensing uncertainty is disclosed; no public-domain claim is made.
- `dependency_license_inventory.json` records installed version and upstream license metadata excerpts for **38 pinned dependencies**. Review full upstream notices/redistribution obligations before packaging or redistributing dependencies; metadata alone is not a compatibility determination. Do not ship the virtual environment.
- Existing credentials were not read, changed or published. No private invoice or live restaurant data was used. No real-world forecast accuracy, savings, optimal allocation or production readiness is claimed.

## Product limits to disclose

The recordable path is a single fixed-recipe synthetic SKU using canonical imported history in a disposable demo database. Historical pizza Explore remains a separate fictional dataset. The normal importer/backend is not a verified Toast/Square adapter or connected upload-to-planner flow. Coverage/menu forms, persisted operational stock, restaurant authentication/isolation, backups, live POS, holidays and stockout-adjusted demand are unfinished. Multi-SKU backend allocation uses deterministic alphabetical order, not profit optimization; the demo UI exposes one SKU only.

Publishing readiness is blocked by the decisions above, even though the local deterministic operations flow can be demonstrated.
