# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Single-file Streamlit app ("WC26 AI Command Center") that predicts World Cup 2026 group-stage
matches using a Poisson goal model. There is no package structure — `app.py` is the entire app.

## Commands

```bash
pip install -r requirements.txt
streamlit run app.py
```

There are no tests or linters configured. To sanity-check changes without launching the UI:

```bash
python -m py_compile app.py
```

## Architecture

- **`Fase_grupos.txt`** — raw input (CSV despite the `.txt` extension): one row per fixture with
  team attributes `OV` (offensive value), `DV` (defensive value), `MV` (market value, M€), and
  `FA` (acclimatization factor), each suffixed `_A` (home) / `_B` (away).
- **`soccer_poisson_model.ipynb`** — the offline notebook that reads `Fase_grupos.txt`, computes
  lambdas and Poisson outcome probabilities for every fixture, and writes the result to
  `predicciones_fase_grupos.csv`. Regenerate this CSV here if the underlying model/data changes.
- **`predicciones_fase_grupos.csv`** — pre-computed predictions for all 72 group-stage matches;
  loaded by the app via `load_data()` and is what powers the Dashboard, Team Analytics, and
  Predictions Table pages.
- **`app.py`** — the Streamlit app. Key things to know:
  - The Poisson lambda formula (`calc_lambdas`, and re-implemented inline in the "Predictor de
    Partido" page) is duplicated from the notebook:
    `λ = (OV/100)^α × (100/DV_rival)^β × (MV/MV_ref)^γ × FA × k`. Sidebar sliders (`alpha_s`,
    `beta_s`, `gamma_s`, `k_s`) let users override the notebook's defaults (`ALPHA, BETA, GAMMA, K`
    module constants) at runtime — if you change the formula, update it in both the "Fixture
    oficial" and "Partido personalizado" branches of the Predictor page, since they're separate
    code paths, not a shared call.
  - `MV_REF` (mean market value across the tournament) is computed once at module scope from
    `load_raw()` (i.e. from `Fase_grupos.txt`, not the predictions CSV) and reused everywhere a
    lambda is recalculated.
  - Navigation is a single `st.radio` in the sidebar driving an `if/elif` chain — there's no
    multipage routing; each "page" is a top-level branch in `app.py`.
  - `FLAGS` is a hardcoded dict mapping Spanish team names to emoji flags; any new team in the
    data needs an entry here or it falls back to a generic ⚽.
  - `st.cache_data` is used on the loaders (`load_data`, `load_raw`) and `top_winners` — keep this
    in mind when changing CSV-reading logic, since Streamlit will cache by function args/source.

## Bayesian knockout model (dieciseisavos onward)

The group-stage model above is static (pre-tournament profile, never updates). For the knockout
rounds there's a second, independent model living alongside it in the same `app.py`:

- **`resultados_reales.csv`** — actual goals for/against (group stage only) for the 32 teams that
  qualified to the knockout stage, one row per team-match. Frozen historical data; don't edit by
  hand — see `poisson_gamma_model.ipynb` for provenance.
- **`poisson_gamma_model.ipynb`** — derives a Poisson-Gamma empirical-Bayes hyperprior (`a0/b0` for
  attack, `a0/b0` for defense, `mu_global`) from `resultados_reales.csv` via method-of-moments, and
  writes it to `hiperprior_bayesiano.json`. This hyperprior is computed **once** and frozen for the
  rest of the tournament — re-run this notebook only if you want to rebuild the reference population
  from scratch, not after every knockout match.
- **`hiperprior_bayesiano.json`** — documentación de referencia; ya **no es leído por `app.py`**.
  Los parámetros se derivaban de un Empirical Bayes global, pero se reemplazó por un prior
  implícito por equipo (ver `calcular_posteriors()`).
- **`resultados_eliminacion.json`** — append-only log of real knockout results entered through the
  app's "🎲 Eliminación Directa" page (`guardar_resultado_eliminacion`). Starts as `[]`.
- **`calcular_posteriors()`** in `app.py` is the actual online-update step: it aggregates
  `resultados_reales.csv` (group stage) per team, then adds goals from `resultados_eliminacion.json`
  (knockout results) to the same counters. The posterior rate is simply
  `goles_totales / partidos_totales` — each team's group-stage data acts as its own implicit prior,
  no global shrinkage. `mu_global` is computed live from the CSV as the mean group-stage goals per
  match (used to normalize lambdas). `equipos_vivos()` derives who's still alive by walking the
  same JSON log for losers (knockout = single elimination). Penalty-shootout winners are tracked via
  `ganador_penales` but penalty goals are never counted — only regulation/extra-time goals feed the
  rate. This subsystem reuses `analyze_match`/`score_matrix_chart`/`prob_donut`/`FLAGS` from the
  group-stage model.
- `BRACKET_R32` in `app.py` hardcodes the confirmed Round-of-32 matchups; pairings for
  octavos/cuartos/semifinal/final are *not* hardcoded — those rounds let the user pick any two
  living teams manually by design.

### Persistence across Streamlit Cloud redeploys

Streamlit Community Cloud's container disk is ephemeral: any push to the repo triggers an
auto-redeploy that re-clones the repo from scratch, wiping anything the running app had only
written to local disk. Since `guardar_resultado_eliminacion`/`eliminar_resultado_eliminacion` write
to the local `resultados_eliminacion.json`, that alone is not durable — `sync_resultados_a_github`
also pushes the updated file straight to `GITHUB_OWNER/GITHUB_REPO` (`NataelM/wc26_app`, branch
`master`) via the GitHub Contents API, so results survive redeploys. This requires a `GITHUB_TOKEN`
(GitHub PAT with `repo` scope) set as a Streamlit Cloud secret — without it, saves/deletes still
work locally for that session but `sync_resultados_a_github` returns `(False, ...)` and the UI
surfaces a warning that the result will be lost on the next redeploy.

## Requirements / compatibility notes

- Requires `streamlit>=1.32.0` for `st.dataframe(..., hide_index=True)` — older Streamlit
  (pre-1.25-ish) doesn't support that kwarg and raises a `TypeError` at runtime, not at import time.
- Requires `pandas>=2.0.0`; no use of pandas APIs removed in 2.0 (no `.append`, `.iteritems`, `.ix`).
