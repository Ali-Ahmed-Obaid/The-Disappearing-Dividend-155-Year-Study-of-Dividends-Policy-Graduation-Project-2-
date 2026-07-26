# The Disappearing Dividend
### 155 Years of US Corporate Payout Policy, 1871–2023 — and What the Gulf Model Does Differently

**Graduation Project · Financial Policy · Dr. Mohammed Alzahrani**
**Ali Ahmed Obaid · 201933250**
**KFUPM Business School (KBS) · King Fahd University of Petroleum & Minerals**

&lt;p align="center"&gt;
  &lt;a href="Graduation%20Project%202%20-%20Ali%20Obaid/Dashboard.html"&gt;
    &lt;img src="https://img.shields.io/badge/🌐_Live-Dashboard-0A6B78?style=for-the-badge" alt="Dashboard"&gt;
  &lt;/a&gt;
  &lt;a href="Graduation%20Project%202%20-%20Ali%20Obaid/Report.pdf"&gt;
    &lt;img src="https://img.shields.io/badge/📄_Report-PDF-1A2833?style=for-the-badge" alt="Report"&gt;
  &lt;/a&gt;
  &lt;a href="Graduation%20Project%202%20-%20Ali%20Obaid/Presentaion.pdf"&gt;
    &lt;img src="https://img.shields.io/badge/🎯_Slides-PDF-B8862B?style=for-the-badge" alt="Slides"&gt;
  &lt;/a&gt;
  &lt;a href="Graduation%20Project%202%20-%20Ali%20Obaid/Comperhansive%20Excel%20Model.xlsx"&gt;
    &lt;img src="https://img.shields.io/badge/📊_Excel-Model-217346?style=for-the-badge" alt="Excel Model"&gt;
  &lt;/a&gt;
&lt;/p&gt;

---

## The finding, in two numbers

&gt; In the **Great Depression**, S&P earnings fell **72%** and the dividend fell **49%**.
&gt; In the **global financial crisis**, earnings fell **79%** and the dividend fell **4%**.

Somewhere between those two crises the dividend stopped being a share of profit and became something closer to a fixed claim. This project dates that change, measures it, and explains it.

---

## Headline results

| Measure | 1871–1900 | 2009–2023 |
|---|---|---|
| Median payout ratio | **71.7%** | **39.8%** |
| Median dividend yield | **4.8%** | **2.0%** |
| Smoothing ratio — sd(Δdiv) ÷ sd(Δearn) | **0.82** | **0.09** |
| Lintner speed of adjustment | **0.36** (mean, pre-1982) | **0.09** (mean, post-1982) |

| Additional findings | |
|---|---|
| Lintner *c* in 2009–2023 | 0.073, t = 0.89 — **statistically indistinguishable from zero** |
| Implied half-life of dividend adjustment | 3.4 years → 5.9 years |
| S&P 500 firms currently paying a dividend | 82.8% (386 of 466) |
| Utilities paying / Information Technology paying | 100% / 59% |
| Life-cycle test: firms &lt;25y vs 100–150y paying | 75% → **98%** |
| Dividend yield → 10-yr forward real return | R² = 0.124 (1/CAPE: R² = 0.283) |

---

## The argument

1. **The dividend changed character, not just level.** The payout ratio roughly halved — but the collapse in *responsiveness to earnings* is the larger and more interesting change.
2. **The break is datable to the early 1980s.** The Lintner speed of adjustment sat between 0.28 and 0.44 in every era from 1871 to 1981 — five eras, 110 years, all significant, all close to Lintner's own 1956 estimate of ~0.30. Since 1982 it has averaged 0.09.
3. **1982 is not arbitrary.** SEC Rule 10b-18 created a safe harbour that made open-market buybacks legally practical. The variable component of shareholder return moved there; the dividend was left carrying only the signal.
4. **Lintner was right about what managers want.** They want to smooth. What changed is that after 1982 they finally had an instrument that let them smooth *completely*.
5. **Payout policy is downstream of ownership.** Saudi Aramco, with a sovereign holding ~97.5% of its register, distributed 92% of cumulative free cash flow and answered its flexibility problem with a *second dividend* rather than a buyback. The US pattern is not a law of finance.

---

## Data — all public, all real

**~21,000 data points across five public datasets. Nothing estimated, simulated or reconstructed.**

| Dataset | Contents | Coverage |
|---|---|---|
| [Shiller S&P 500 series](https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv) | Price, dividend, earnings, CPI, 10-year rate, CAPE — monthly | Jan-1871 → Jun-2023 (**1,830 obs**) |
| [S&P 500 constituents](https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv) | GICS sector, sub-industry, date added, year founded | Current |
| [S&P 500 financials](https://raw.githubusercontent.com/datasets/s-and-p-500-companies-financials/main/data/constituents-financials.csv) | Price, P/E, P/B, dividend yield, EPS, market cap | Current (**466 matched**) |
| [US 10-year Treasury](https://raw.githubusercontent.com/datasets/bond-yields-us-10y/main/data/monthly.csv) | Constant maturity yield, monthly | 1953 → 2026 |
| [Saudi Aramco results](https://www.aramco.com/en/investors/annual-report) | Free cash flow and distributions | FY2019 → FY2025 |

---

## Repository contents
Graduation Project 2 - Ali Obaid/
├── Codes Files/                    → Python analysis scripts (engine.py, export.py)
├── Data Files/                     → Raw + processed datasets (14 Excel/CSV files)
├── Power BI/                       → Star schema, DAX measures (~55), build guide
├── Comperhansive Excel Model.xlsx  → Linked Excel financial model
├── Dashboard.html                  → Interactive web dashboard (open in browser)
├── Presentaion.pdf                 → 20-slide defence deck
└── Report.pdf                      → 17-page written report with references


### Deliverables

| File | What it is | How to view |
|---|---|---|
| [Dashboard.html](Graduation%20Project%202%20-%20Ali%20Obaid/Dashboard.html) | 7-page interactive web dashboard | Click badge above or download & open in browser |
| [Report.pdf](Graduation%20Project%202%20-%20Ali%20Obaid/Report.pdf) | Full written report, 17 pages | Click badge above |
| [Presentaion.pdf](Graduation%20Project%202%20-%20Ali%20Obaid/Presentaion.pdf) | Defence deck, 20 slides | Click badge above |
| [Comperhansive Excel Model.xlsx](Graduation%20Project%202%20-%20Ali%20Obaid/Comperhansive%20Excel%20Model.xlsx) | Financial model + linked data | Click badge above or download |

### Power BI

A `.pbix` is a compiled binary and cannot be authored outside Power BI Desktop. `Power BI/` contains everything that goes into one — a **15-table star schema** (3,546 rows), a **DAX library of ~55 measures**, and a **build guide** specifying every page, visual and field placement. Roughly 90 minutes to assemble. The HTML dashboard shows the same seven pages and runs live.

---

## Method

- **Lintner partial adjustment** — ΔDPS = a + c × (target payout × EPS − lagged DPS), estimated separately in eight eras and pooled pre/post-1982 with a common target
- **Rolling 20-year smoothing ratio** — sd(dividend growth) ÷ sd(earnings growth), imposing no era boundaries, to confirm the break is not an artefact of chosen dates
- **Crisis drawdown analysis** — peak-to-trough falls in earnings, dividends and price across nine episodes, 1873–2020
- **Predictive regression** — subsequent 10-year annualised real total return on starting dividend yield (reported as descriptive; see limitations)
- **Cross-sectional tests** — payer share by GICS sector and by firm age, testing DeAngelo, DeAngelo & Stulz (2006)

---

## Limitations

Stated in full in Section 8 of the report. In short:

- **Index-level, not firm-level** for the long run — cannot separate composition change from firms changing policy
- **No repurchase series** — the 1982 interpretation is an inference from timing, not a direct test. This is the principal gap and the obvious extension
- **Overlapping windows** in the predictive regression — effective sample nearer 15 than 1,590; no significance claimed
- **Era boundaries are chosen, not estimated** — the rolling analysis is included precisely so the finding doesn't depend on them
- **Cross-section is a snapshot** of current index members, subject to survivorship

---

## Reproducing

```bash
pip install pandas numpy openpyxl
cd "Graduation Project 2 - Ali Obaid/Codes Files"
python engine.py       # prints every result table
python export.py       # writes all CSVs + the dashboard payload

License
Academic project. Analysis is original work built on public data. Reuse with attribution.
