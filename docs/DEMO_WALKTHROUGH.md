# Three-minute walkthrough — prepare, do not claim submitted

This script demonstrates the working local prototype. It is not a recording. No live Meta result exists. All restaurant results shown are fictional or explicitly synthetic.

Start the existing app with `sh run.sh` from the project folder. Open http://127.0.0.1:8501. For a recording, keep your own launch window open; a chat-hosted server may stop with its task. No Terminal automation or auto-start service was installed.

| Time | Show / action | Say |
|---|---|---|
| 0:00–0:20 | App title, Explore | “Restaurant Prep Lab helps an operator anticipate demand and check whether their current stock and preparation time can support it. Pizza is our example; the workflow is about restaurant operations.” |
| 0:20–0:45 | Explore sales/bestseller/rush charts | “This historical dashboard uses a fictional restaurant dataset, not actual customer results. It shows what sold and when orders arrived. Revenue is sales, not profit. Our canonical importer separately validates IDs, quantities, refunds and timestamps.” |
| 0:45–1:20 | Click Prep Planner; show synthetic warning and four observations | “This is a separate, explicitly synthetic planning scenario. Four comparable days had 26, 28, 30 and 32 fulfilled portions. The transparent average forecasts 29 for the shown demo date. The baseline uses only information available at its cutoff and reports insufficient history rather than inventing a forecast.” |
| 1:20–2:00 | Show fixed recipe. Leave dough 10,000 g, cheese 2,000 g, sauce 3,000 g, time 60 min. Check review box; Calculate prep scenario. | “The recipe stays fixed: 250 grams dough, 100 grams cheese, 80 grams sauce and two prep minutes per portion. After confirming counted demo stock, the system calculates full-demand requirements. We need 2,900 grams of cheese but have 2,000: a 900-gram shortage. Current resources support 20 portions, leaving nine expected portions uncovered.” |
| 2:00–2:25 | Change cheese to 3,500 g; Calculate again | “Here is a hypothetical replenishment, not an automatic purchase. Now all 29 portions fit within stock and 58 preparation minutes. We changed a resource assumption, not the recipe. Nothing is written to live inventory.” |
| 2:25–2:50 | Meta Evidence screen, show actual status; do not initiate a paid call during rehearsal | “The intended Meta workflow is invoice evidence, human correction, then validated inputs to deterministic planning. The page now supports a gated synthetic-note extraction and confirmation handoff, but no live response has been verified yet. We do not present mocked tests as model output.” |
| 2:50–3:00 | Return to planner | “The working core connects a demand estimate to ingredient shortages and a feasible prep scenario. The next integration gates are actual source validation and verified Meta evidence.” |

Before recording: confirm the browser is showing this run, hide personal tabs/notifications, rehearse under three minutes, and verify no secrets or private documents are visible. Do not describe the app as production ready, claim measured waste savings, imply the two datasets are one restaurant, or say it already runs live POS/Meta integrations.

Expected scenario checks: 29 expected; default 20 feasible / 9 unmet / 40 minutes; cheese shortage 900 g. With 3,500 g cheese: 29 feasible / 0 unmet / 58 minutes. With only 10 preparation minutes: at most 5 portions regardless of ingredient surplus.
