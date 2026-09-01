# HSE Risk Intelligence

**Analytics & Decision-Support Prototype — Synthetic Demo Data**

This local Streamlit application is a compact interview demonstration for exploring Health, Safety and Environment (HSE) data in a pharmaceutical context. It is not an autonomous safety system and must not be used as a substitute for qualified HSE judgement.

## Features

The application has exactly three pages:

1. **Operational HSE Overview** — KPI cards, four specified charts and a programmatically derived pattern signal over 104 synthetic reports. A refresh control generates a new reproducible demo scenario.
2. **Hazard & Near-Miss Assessment** — keyword-assisted category suggestion with user override, validated 1–5 inputs, a highlighted 5×5 risk matrix, potential hierarchy-of-controls recommendations and suggested CAPA items.
3. **Environmental Sustainability & Data Exploration** — January–August synthetic indicators, transparent anomaly checks and a two-component PCA of report features.

## Architecture

The prototype is intentionally contained in `app.py`. Small functions generate data, calculate risk, classify descriptions, calculate anomalies, build CAPA suggestions and render each page. Streamlit provides navigation and presentation; pandas/numpy provide data handling; Plotly provides charts; scikit-learn provides standardization and PCA. No API, key, cloud service, authentication or production data is used.

## Calculations

### Risk scoring

`risk_score = likelihood × severity`, where both inputs are integers from 1 to 5. Scores 1–4 are Low, 5–9 Medium, 10–16 High and 17–25 Critical. Action priorities are rule-based guidance; final assessment remains with qualified HSE personnel.

### Keyword classification

The description is converted to lowercase and checked against visible keyword lists (for example, `solvent`, `acid`, `spill` and `fumes` suggest Chemical). The category with the most matches is suggested. If nothing matches, Mechanical is a neutral prototype default explicitly marked for review. The user can always override the suggestion.

### Anomaly detection

For every environmental metric:

`deviation (%) = (latest − mean of preceding 3 months) / mean of preceding 3 months × 100`

The metric is flagged only when the absolute deviation is greater than 15%. The app displays the latest value, baseline and deviation. A flag recommends investigation of operational or measurement changes; it does not imply causation.

### PCA pipeline

Six report features are used: likelihood, severity, people exposed, downtime hours, environmental impact score and repeat count. `StandardScaler` first puts them on comparable scales. `PCA(n_components=2)` then creates PC1 (the direction with greatest variance) and PC2 (the next greatest, orthogonal direction). Explained variance is displayed. The plot is exploratory and neither proves clusters nor explains causes.

## Human in the loop

Calculated values are visually separated from potential controls and CAPA recommendations. All recommendations require review, adaptation and approval by qualified HSE personnel using site procedures.

## Limitations

- All records are synthetic. Each refresh uses a deterministic seed derived from base seed 42, so a scenario remains internally consistent while refreshed scenarios produce different values.
- The keyword classifier understands only listed words and not full context, negation or nuanced hazards.
- Risk bands simplify site-specific risk methodologies.
- The days-without-LTI KPI is a clearly labelled proxy because the demo data has no separate lost-time field.
- The anomaly rule is a simple comparison, not forecasting or root-cause analysis.
- PCA is sensitive to the selected inputs and provides no causal conclusion.

## Install and run

Python 3.10 or newer is recommended.

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local address, normally `http://localhost:8501`, which opens the application in a browser.

## Vercel deployment

`Dockerfile.vercel` packages the Streamlit server for Vercel's container runtime. Vercel supplies the listening port through `PORT`; the container command binds Streamlit to that port and to all interfaces. Local use remains unchanged.

## Possible production extensions

Subject to governance and validation: controlled data ingestion, role-based access, audit trails, site-specific risk matrices, workflow integration, data-quality checks, validated model monitoring and formal HSE approval gates. These are intentionally outside this prototype.
