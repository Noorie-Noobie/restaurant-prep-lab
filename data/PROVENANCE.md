# Dataset provenance and interpretation

- Source: `gt::pizzaplace`, maintained in the gt package by Posit and contributors.
- Author documentation: https://gt.rstudio.com/reference/pizzaplace.html
- Download mirror: https://vincentarelbundock.github.io/Rdatasets/csv/gt/pizzaplace.csv
- Downloaded: 2026-10-28. Original file retained in `raw/pizzaplace.csv`.
- SHA256: `243425c7184d31b35b09ae72c468154b1fb3434ec5d4f5cd32c8beb89d1b8801`
- gt package license: MIT, https://gt.rstudio.com/LICENSE.html ; original notice retained in `raw/LICENSE-gt.txt`. Rdatasets does not definitively resolve every individual dataset license; this uses original package documentation/notice rather than claiming public domain.

**Fictional dataset**, somewhere in the US; not a real restaurant, not SF observations. No customer identifiers. Covers 2015-01-01 to 2015-12-31 with 358 observed dates. Seven missing calendar dates are not proven zero-sales/open days. Timezone unspecified; local wall-clock values remain unconverted.

49,574 pizza lines; 21,350 order IDs; 32 names; 91 name-size SKUs; revenue $817,860.05. Each row is one pizza. Source rownames become line IDs. Repeated business rows are retained because they can represent multiple identical pizzas. Status is assumed completed from a sales-only source, with that assumption stored explicitly; source has no cancellations/refunds/status column.

SQLite fields: `line_id`, `order_id`, `ordered_at`, `timezone`, `item_id` (name + size), `item_name`, `size`, `category`, `quantity` (=1), `unit_price_cents`, `status`, `status_basis`. Money uses integer cents. The metadata table records raw hash and provenance. Original CSV is never changed by build scripts.

Explore uses all dishes. Planning scope selects the top seven names by whole-year unit count (alphabetical tie break), retaining size-specific SKUs. This is demo scope selection, not an unbiased forecast evaluation protocol. Train/test windows and historical menu selection must be defined before forecasting.

Source documentation lists ingredients but not recipe weights, costs, current inventory, service capacity or preparation minutes. Any such inputs added later must be visibly labeled demo assumptions and confirmed before use. Do not claim measured waste reductions or actual business savings.
