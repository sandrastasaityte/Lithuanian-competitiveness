# Lithuanian Competitiveness Analysis

## Overview

This project develops an economist-oriented analytical framework for assessing **Lithuania's international competitiveness, structural transformation, external competitive pressure, investment dynamics and sector-level vulnerability**.

The project combines trade, revealed comparative advantage, trade balances, Chinese competitive pressure, foreign direct investment, technological upgrading and structural vulnerability into an integrated sector-level risk framework.

The objective is not simply to describe Lithuania's exports, but to identify:

* Which sectors have a comparative advantage
* Which sectors are gaining or losing competitiveness
* Where external competitive pressure is increasing
* Which sectors are vulnerable to structural change
* Whether FDI is supporting technological upgrading
* Which sectors face the greatest long-term competitiveness risks
* Where policy intervention may be most valuable

---

# 1. Research Questions

The project addresses six main economic questions:

### 1. International competitiveness

Which Lithuanian sectors demonstrate a **revealed comparative advantage (RCA)**?

### 2. Trade performance

Which sectors generate relatively strong or weak **relative trade balances (RTB)**?

### 3. External competitive pressure

Which Lithuanian sectors face increasing competitive pressure from China?

### 4. Foreign investment

Is FDI supporting structural and technological upgrading?

### 5. Structural transformation

Are Lithuanian sectors moving towards higher-value and more technologically intensive activities?

### 6. Vulnerability and risk

Which sectors are most exposed to structural, external and competitiveness risks?

---

# 2. Analytical Framework

The project is organised into five analytical layers:

```text
Trade Data
    │
    ├── Export Competitiveness
    │       ├── RCA
    │       ├── RCA Change
    │       └── RCA Trend
    │
    ├── External Competitive Pressure
    │       ├── China Pressure Index
    │       └── China Pressure Trend
    │
    ├── Investment & Structural Change
    │       ├── FDI
    │       └── Structural Change
    │
    ├── Structural Vulnerability
    │       └── Vulnerability Index
    │
    └── Integrated Risk
            └── Total Risk Model
```

The final objective is to move from **descriptive trade statistics** to an integrated assessment of Lithuania's structural competitiveness.

---

# 3. Project Structure

```text
Lithuanian competetiveness/
│
├── README.md
│
├── data.py
│
├── Lithuania_Competitiveness_Model.xlsx
│
├── export competitiveness/
│   ├── Export share.py
│   ├── RCA change.py
│   ├── RCA trend.py
│   └── outputs/
│
├── External Competitive Pressure/
│   ├── China Pressure Index.py
│   ├── China pressure trend.py
│   └── outputs/
│
├── Risk/
│   ├── FDI.py
│   ├── Structural change.py
│   └── outputs/
│
└── Structural Transformation/
    ├── Total risk.py
    ├── Vulnerability.py
    └── outputs/
```

---

# 4. Core Data Model

The central dataset is:

```text
Lithuania_Competitiveness_Model.xlsx
```

The model is designed around sector-year observations.

Important variables include:

| Variable                     | Description                    |
| ---------------------------- | ------------------------------ |
| `Year`                       | Observation year               |
| `SITC_Group`                 | SITC sector classification     |
| `RCA`                        | Revealed Comparative Advantage |
| `RTB`                        | Relative Trade Balance         |
| `FDI_Inflow_EUR`             | Foreign direct investment      |
| `Tech_Level`                 | Technology classification      |
| `China_EU_Trade_Balance_EUR` | China-EU trade balance         |
| `Overlap_Flag`               | Competitive product overlap    |
| `Export_Share_Pct`           | Sector share of exports        |
| `Major_Firms_Count`          | Number of major firms          |

Derived indicators are calculated by the individual analytical modules.

---

# 5. Sector Classification

The project uses broad SITC groups:

| SITC | Sector                     |
| ---: | -------------------------- |
|    0 | Food                       |
|    1 | Crude Materials            |
|    2 | Minerals                   |
|    3 | Fuels                      |
|    4 | Animal/Vegetable Oils      |
|    5 | Chemicals                  |
|    6 | Manufactured Goods         |
|    7 | Machinery                  |
|    8 | Miscellaneous Manufactures |
|    9 | Commodities                |

These broad groups provide a high-level view of Lithuania's sectoral competitiveness.

For more detailed future analysis, the model can be extended to SITC 2-digit or 3-digit classifications.

---

# 6. Export Competitiveness

## Revealed Comparative Advantage

RCA is used to identify whether Lithuania is relatively specialised in a particular sector compared with the reference economy.

The standard interpretation is:

```text
RCA > 1
    Comparative advantage

RCA < 1
    Comparative disadvantage

RCA = 1
    Neutral position
```

The project does not treat RCA as a measure of absolute productivity.

Instead, RCA measures **relative export specialisation**.

---

# 7. RCA Trend Analysis

`RCA trend.py` evaluates whether comparative advantage is:

* Improving
* Deteriorating
* Stable

The model also calculates:

* First observed RCA
* Latest RCA
* Average RCA
* Maximum RCA
* Minimum RCA
* Long-term RCA change
* Year-on-year RCA change

Sectors are then classified into positions such as:

```text
Strong and Improving
Advantage but Deteriorating
Weak but Improving
Weak and Deteriorating
Stable
```

This is more informative than looking at a single year's RCA.

---

# 8. External Competitive Pressure

## China Pressure Index

The China module measures potential competitive pressure using:

* China-related trade pressure
* Lithuanian comparative disadvantage
* Product/sector overlap

The index is normalised onto a comparable scale.

The resulting score is classified as:

```text
0–24     Low
25–49    Moderate
50–74    High
75–100   Very High
```

The China indicator should be interpreted as a **model-based competitive pressure measure**, rather than a direct causal estimate of Chinese competition.

---

# 9. FDI Analysis

`FDI.py` examines whether foreign investment is associated with structural changes in Lithuanian sectors.

The analysis considers:

* FDI inflows
* FDI changes
* FDI percentage changes
* FDI deterioration
* Technology level
* Technology upgrading
* RCA development

An important methodological principle is:

> High FDI does not automatically mean low risk.

Large FDI can be associated with either:

* technological upgrading,
* productivity improvements,
* export expansion,

or:

* foreign dependence,
* concentration,
* declining investment,
* limited domestic value added.

Therefore the model focuses on the **direction and structural implications of FDI**, not simply its size.

---

# 10. Structural Transformation

`Structural change.py` measures changes in the underlying economic structure.

The model considers:

* Technology upgrading
* FDI development
* RCA development

The objective is to identify whether sectors are moving towards stronger structural positions.

The model distinguishes between:

```text
Structural Upgrading
Technology Upgrading but RCA Weakening
RCA Improving but Technology Weakening
Structural Deterioration
Limited Structural Change
```

This distinction is important because technological improvement and export competitiveness do not necessarily move together.

---

# 11. Structural Vulnerability

`Vulnerability.py` provides a separate assessment of sectoral fragility.

The vulnerability framework considers seven dimensions:

| Component              |   Weight |
| ---------------------- | -------: |
| Export concentration   |      20% |
| Firm concentration     |      15% |
| RCA weakness           |      20% |
| Trade balance weakness |      10% |
| China pressure         |      15% |
| FDI deterioration      |      10% |
| Technology weakness    |      10% |
| **Total**              | **100%** |

The resulting score is:

```text
0–24     Very Low Vulnerability
25–39    Low Vulnerability
40–59    Moderate Vulnerability
60–74    High Vulnerability
75–100   Very High Vulnerability
```

The purpose is to identify sectors where several vulnerabilities occur simultaneously.

---

# 12. Total Risk Model

`Total risk.py` provides the integrated competitiveness-risk framework.

The current model combines:

| Risk dimension                 |   Weight |
| ------------------------------ | -------: |
| External competitiveness       |      25% |
| China competitive pressure     |      20% |
| FDI / investment deterioration |      15% |
| Structural transformation      |      20% |
| Scale vulnerability            |      10% |
| Competitiveness volatility     |      10% |
| **Total**                      | **100%** |

The result is a:

## Total Competitiveness Risk Score

from 0 to 100.

Interpretation:

```text
0–24     Very Low Risk
25–39    Low Risk
40–59    Moderate Risk
60–74    High Risk
75–100   Very High Risk
```

---

# 13. Risk Drivers

The model also identifies the dominant source of risk for each sector.

Possible drivers include:

```text
External Competitiveness
China Pressure
FDI
Structural Transformation
Scale Vulnerability
Volatility
```

This is important because two sectors can have identical total risk scores while requiring completely different policy responses.

For example:

```text
Sector A
High risk → China pressure

Sector B
High risk → Technology weakness

Sector C
High risk → Falling RCA

Sector D
High risk → FDI deterioration
```

The policy implications are therefore different.

---

# 14. Policy Priority

The model converts the analytical results into broad policy priorities.

Examples include:

```text
Critical Intervention
High Policy Priority
Monitor Closely
Competitive Strength
Monitor
```

This should not be interpreted as an automatic policy recommendation.

Instead, it provides a **screening mechanism for identifying sectors requiring deeper economic analysis**.

---

# 15. Outputs

The project generates Excel analysis files containing:

### Detailed Analysis

Sector-year level calculations.

### Sector Summary

Long-term sector-level indicators.

### Economic Interpretation

Automatically generated interpretation of the model results.

### Risk Tables

Separate lists of:

* Very high-risk sectors
* High-risk sectors
* Deteriorating sectors
* Improving sectors
* Technology-upgrading sectors

### Charts

The model generates visualisations including:

* RCA trends
* RCA rankings
* China pressure trends
* FDI trends
* Structural transformation
* Vulnerability rankings
* Vulnerability changes
* Risk rankings
* Risk drivers
* Average risk over time

---

# 16. Python Environment

The project uses Python and the following main libraries:

```text
pandas
numpy
matplotlib
openpyxl
```

Install them with:

```bash
python -m pip install pandas numpy matplotlib openpyxl
```

If using the PyCharm virtual environment:

```bash
.venv\Scripts\python.exe -m pip install pandas numpy matplotlib openpyxl
```

---

# 17. Running the Model

The central model should be generated/updated before running the analytical modules.

Recommended sequence:

```text
1. data.py

2. Export share.py

3. RCA change.py

4. RCA trend.py

5. China Pressure Index.py

6. China pressure trend.py

7. FDI.py

8. Structural change.py

9. Vulnerability.py

10. Total risk.py
```

The final `Total risk.py` should be treated as the highest-level analytical output.

---

# 18. Methodological Principles

Several principles guide the analysis.

### 18.1 Relative competitiveness ≠ productivity

RCA indicates export specialisation, not productivity directly.

### 18.2 FDI ≠ automatically positive

Investment quality, direction and technological content matter.

### 18.3 Trade deficits ≠ automatically failure

A trade deficit can reflect productive investment or imported intermediate inputs.

### 18.4 China pressure ≠ causality

The China Pressure Index identifies potential competitive exposure. It does not establish that Chinese imports caused Lithuanian firms to lose market share.

### 18.5 Risk scores are model-based

Weights and normalisation methods are analytical assumptions and should be tested through sensitivity analysis.

### 18.6 Structural transformation is dynamic

The most important question is not only:

> "Where is Lithuania competitive today?"

but also:

> "Where is Lithuania becoming more or less competitive?"

---

# 19. Limitations

The current framework has several limitations.

## Data limitations

Results depend on the quality, coverage and consistency of the underlying sector-year data.

## Sector aggregation

Broad SITC groups can hide important differences between individual industries.

## Weight selection

Risk weights are analytical assumptions rather than officially established economic weights.

## Normalisation

Min-max normalisation makes indicators comparable but can be sensitive to extreme observations.

## Causality

The framework identifies associations and risk patterns. It does not by itself establish causal relationships.

## Missing variables

Future versions could incorporate:

* Labour productivity
* Unit labour costs
* Wages
* Employment
* R&D expenditure
* Patent activity
* Energy intensity
* Carbon intensity
* Human capital
* Export destination concentration
* Import dependence
* Global value-chain participation
* Domestic value added
* Productivity growth
* Firm entry and exit

---

# 20. Future Development

The next stage of the project should move towards a more advanced **Lithuanian Competitiveness Dashboard**.

Potential additions include:

### Economic Complexity

Add:

* Economic Complexity Index
* Product Complexity
* Product-space analysis

### Export Diversification

Measure:

* Herfindahl-Hirschman Index
* Export destination concentration
* Product concentration

### Productivity

Add:

* Labour productivity
* Total factor productivity
* Productivity growth

### Innovation

Add:

* R&D intensity
* Patents
* High-tech exports
* Knowledge-intensive employment

### Labour Market

Add:

* Employment growth
* Wage growth
* Labour shortages
* Skills intensity

### Energy Competitiveness

Add:

* Energy prices
* Energy intensity
* Import dependence
* Carbon intensity

### European Benchmarking

Compare Lithuania with:

* Latvia
* Estonia
* Poland
* Czechia
* Slovakia
* Slovenia
* EU average

---

# 21. Sensitivity Analysis

A professional version of the model should test whether the conclusions depend heavily on the selected weights.

For example:

```text
Baseline
25% competitiveness
20% China
15% FDI
20% structural transformation
10% scale
10% volatility
```

could be compared with:

```text
External-risk scenario
20% competitiveness
30% China
15% FDI
15% structural transformation
10% scale
10% volatility
```

and:

```text
Structural-transformation scenario
20% competitiveness
15% China
15% FDI
30% structural transformation
10% scale
10% volatility
```

If the same sectors remain high-risk across scenarios, the conclusion becomes considerably more robust.

---

# 22. Research Interpretation

The ultimate objective is to construct a framework capable of answering:

> **Is Lithuania becoming more competitive, more technologically advanced and more resilient, or is its export structure becoming increasingly vulnerable to external competition and structural shocks?**

The project therefore combines:

```text
Competitiveness
      +
Trade performance
      +
External pressure
      +
Investment
      +
Technology
      +
Structural transformation
      +
Vulnerability
      ↓
Total Competitiveness Risk
```

This provides a framework for analysing Lithuania not only as an exporter, but as a **small open economy undergoing structural transformation within European and global value chains**.

---

# 23. Author

**Sandra Stasaityte**

Economics / Finance / Economic Analytics Project

Focus areas:

* International economics
* Competitiveness
* Trade economics
* Structural transformation
* Foreign direct investment
* Economic risk
* Data analytics
* Python
* Excel
* Visualisation

---

# 24. Project Status

**Current stage: Advanced analytical framework**

Implemented:

* Export competitiveness
* RCA analysis
* RCA trend analysis
* China competitive pressure
* China pressure trends
* FDI analysis
* Structural transformation
* Structural vulnerability
* Integrated total risk
* Sector rankings
* Economic interpretation
* Automated Excel outputs
* Automated charts

Planned:

* Sensitivity analysis
* Economic Complexity Index
* Export diversification
* Productivity indicators
* Innovation indicators
* EU benchmarking
* Interactive dashboard
* Econometric analysis
* Robustness testing
* Policy simulation
