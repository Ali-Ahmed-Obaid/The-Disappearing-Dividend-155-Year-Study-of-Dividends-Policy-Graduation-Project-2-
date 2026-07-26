# The Disappearing Dividend
### 155 Years of US Corporate Payout Policy, 1871–2023 — and What the Gulf Model Does Differently

**Graduation Project 2 · Financial Policy**
**Dr. Mohammed Alzahrani** &nbsp;|&nbsp; **Ali Ahmed Obaid · 201933250**
**KFUPM Business School (KBS) · King Fahd University of Petroleum & Minerals**

<p align="center">
  <a href="https://ali-ahmed-obaid.github.io/The-Disappearing-Dividend-155-Year-Study-of-Dividends-Policy-Graduation-Project-2-/Graduation%20Project%202%20-%20Ali%20Obaid/Dashboard.html">
    <img src="https://img.shields.io/badge/Live-Dashboard-0A6B78?style=for-the-badge" alt="Dashboard">
  </a>
  <a href="Graduation%20Project%202%20-%20Ali%20Obaid/Report.pdf">
    <img src="https://img.shields.io/badge/Report-PDF-1A2833?style=for-the-badge" alt="Report">
  </a>
  <a href="Graduation%20Project%202%20-%20Ali%20Obaid/Presentaion.pdf">
    <img src="https://img.shields.io/badge/Slides-PDF-B8862B?style=for-the-badge" alt="Slides">
  </a>
  <a href="Graduation%20Project%202%20-%20Ali%20Obaid/Comprehansive%20Exceel%20Model.xlsx">
    <img src="https://img.shields.io/badge/Excel-Model-217346?style=for-the-badge" alt="Excel Model">
  </a>
</p>

---

## The finding, in two numbers

> In the **Great Depression**, S&P earnings fell **72%** and the dividend fell **49%**.
> In the **global financial crisis**, earnings fell **79%** and the dividend fell **4%**.

Somewhere between those two crises the dividend stopped being a share of profit and became something closer to a fixed claim. This project dates that change, measures it, and explains it.

---

## Headline results

| Measure | 1871–1900 | 2009–2023 |
|---|---|---|
| Median payout ratio | **71.7%** | **39.8%** |
| Median dividend yield | **4.8%** | **2.0%** |
| Smoothing ratio — sd(Δdiv) ÷ sd(Δearn) | **0.82** | **0.09** |
| Lintner speed of adjustment | **0.36** (pre-1982) | **0.09** (post-1982) |

| Additional findings | |
|---|---|
| Lintner *c* in 2009–2023 | 0.073, t = 0.89 — statistically indistinguishable from zero |
| S&P 500 firms currently paying a dividend | 82.8% (386 of 466) |
| Utilities paying / Information Technology paying | 100% / 59% |
| Life-cycle test: firms <25y vs 100–150y paying | 75% → **98%** |

## The argument

1. **The dividend changed character, not just level.** The payout ratio roughly halved — but the collapse in responsiveness to earnings is the larger change.
2. **The break is datable to the early 1980s.** The Lintner speed of adjustment sat between 0.28 and 0.44 in every era from 1871 to 1981. Since 1982 it has averaged 0.09.
3. **1982 is not arbitrary.** SEC Rule 10b-18 made open-market buybacks legally practical. The variable component of shareholder return moved there.
4. **Lintner was right about what managers want.** They want to smooth. After 1982 they finally had an instrument that let them smooth completely.
5. **Payout policy is downstream of ownership.** Saudi Aramco, with a sovereign holding ~97.5% of its register, distributed 92% of cumulative free cash flow and answered its flexibility problem with a second dividend rather than a buyback.

---

## Data — all public, all real

**~21,000 data points across five public datasets. Nothing estimated, simulated or reconstructed.**

| Dataset | Contents | Coverage |
|---|---|---|
| [Shiller S&P 500 series](https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv) | Price, dividend, earnings, CPI, 10-year rate, CAPE | Jan-1871 to Jun-2023 (1,830 obs) |
| [S&P 500 constituents](https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv) | GICS sector, sub-industry, year founded | Current |
| [S&P 500 financials](https://raw.githubusercontent.com/datasets/s-and-p-500-companies-financials/main/data/constituents-financials.csv) | Price, P/E, P/B, dividend yield | Current (466 matched) |
| [US 10-year Treasury](https://raw.githubusercontent.com/datasets/bond-yields-us-10y/main/data/monthly.csv) | Constant maturity yield | 1953 to 2026 |
| [Saudi Aramco results](https://www.aramco.com/en/investors/annual-report) | Free cash flow and distributions | FY2019 to FY2025 |

---





## Repository contents Graduation Project 2 - Ali Obaid/
 ├── Dashboard.html live interactive dashboard, 7 pages

 ├── Report.pdf full written report with references

 ├── Presentaion.pdf defence deck, 20 slides

 ├── Comprehansive Exceel Model.xlsx 14-sheet workbook, all data and results

 ├── Codes Files/ Python analysis scripts

 ├── Data Files/ raw and processed CSVs

 └── Power BI/ star schema, DAX measures, build guide







### Power BI

A `.pbix` is a compiled binary and cannot be authored outside Power BI Desktop. The `Power BI` folder contains everything needed to build one: a 15-table star schema, a DAX library of about 55 measures

---







## Limitations

Stated in full in the report. In short:

- Index-level, not firm-level, for the long-run series — cannot separate composition change from firms changing policy
- No repurchase series — the 1982 interpretation is an inference from timing, not a direct test
- Overlapping windows in the predictive regression — effective sample nearer 15 than 1,590
- Cross-section is a snapshot of current index members, subject to survivorship




## License

Academic project. Analysis is original work built on public data. Reuse with attribution.
