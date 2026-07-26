# Power BI Build Guide
## The Disappearing Dividend — 155 Years of US Payout Policy

**Ali Ahmed Obaid · 201933250 · Financial Policy · Dr. Mohammed Alzahrani · KFUPM**

---

## 0. What this is, and what it is not

A `.pbix` is a proprietary compiled binary — it cannot be authored outside Power BI Desktop. What you have here is everything that goes *into* one:

- **15 CSV tables** shaped as a proper star schema
- **A DAX library** of ~55 measures in `DAX_Measure_Library.txt`
- **This guide**, specifying every page, visual and field placement

Budget about **90 minutes**. The result is yours, and you'll be able to answer "how is the smoothing ratio calculated?" in a defence — which you can't do with a black box.

If you want to see the design target first, open `docs/index.html` — the seven-page HTML dashboard runs the same data.

---

## 1. Load

**Home → Get Data → Text/CSV**, load all 15 files from `powerbi/`.

In **Transform Data**, check these types:

| Column | Type |
|---|---|
| `Dim_Year[YearEndDate]` | **Date** |
| `Fact_Monthly[Date]` | **Date** |
| All `*Key` columns | **Text** or **Whole Number**, consistently |
| Everything numeric | **Decimal Number** |
| `Fact_Firm[Payer]` | **True/False** |

Close & Apply.

**Then mark the date table:** select `Dim_Year` → **Table tools → Mark as date table → YearEndDate**. Skip this and the time-intelligence measures return blanks silently rather than erroring.

---

## 2. Relationships

Model view. All one-to-many, single direction, dimension → fact.

| From (one) | To (many) |
|---|---|
| `Dim_Year[Year]` | `Fact_Annual[YearKey]` |
| `Dim_Year[Year]` | `Fact_Monthly[YearKey]` |
| `Dim_Year[Year]` | `Fact_Rolling[YearKey]` |
| `Dim_Year[Year]` | `Fact_Predictive[YearKey]` |
| `Dim_Era[EraSort]` | `Fact_Era[EraSort]` |
| `Dim_Era[EraSort]` | `Fact_Lintner[EraSort]` |
| `Dim_Sector[SectorKey]` | `Fact_Firm[SectorKey]` |
| `Dim_Company[CompanyKey]` | `Fact_Firm[CompanyKey]` |
| `Dim_AgeBand[AgeBandKey]` | `Fact_Firm[AgeBandKey]` |

`Fact_Crises`, `Fact_Aramco` and `Ref_Findings` stay **disconnected** — they're standalone reference tables. Don't relate them.

**Sort orders that matter:**
- `Dim_Era[Era]` → sort by `EraSort`
- `Dim_AgeBand[AgeBandKey]` → sort by `Sort`

Without these, eras and age bands appear alphabetically and the charts become meaningless.

Hide from report view: every `*Key` column on the fact tables.

---

## 3. Measures

**Home → Enter Data**, name it `_Measures`, Load, delete the placeholder column. Paste from `DAX_Measure_Library.txt` in section order — sections 1–2 first, everything else depends on them.

---

## 4. Theme

**View → Themes → Customize current theme.** Palette matched to the dashboard:

| Slot | Hex | Use |
|---|---|---|
| Primary | `1A2833` | headers, KPI numbers |
| Secondary | `0A6B78` | pre-1982 series, the "old regime" |
| Accent | `B8862B` | post-1982 series, the "new regime" |
| Positive | `1B7F4C` | above-benchmark |
| Negative | `AE3227` | earnings falls, distress |
| Neutral | `6E7A85` | gridlines, secondary text |
| Card background | `F2F6F9` | KPI tiles |

Text → General → **Arial**, size 10. Titles 14 semibold.

**One convention worth keeping throughout:** teal = pre-1982, gold = post-1982. Once the audience learns it on page 2, every later chart reads instantly.

---

## 5. The seven pages

Common header on every page: title left, an `Dim_Era[Era]` slicer and a `Dim_Year[Year]` range slicer right. Sync both (**View → Sync slicers**).

---

### Page 1 — The Finding

*Answers: what changed?*

| Position | Visual | Fields |
|---|---|---|
| Top, 5 cards | Card | `[Median Payout Ratio]`, `[Median Dividend Yield]`, `[Smoothing Ratio]`, `[Speed of Adjustment]`, `[Payer Share]` |
| Centre, large | Line chart | Axis `Dim_Year[Year]`; values `[Payout Ratio]` and `[Dividend Yield]` on secondary axis |
| Right | Multi-row card | `[Headline Payout Change]`, `[Data Coverage]`, `[Smoothing Ratio Label]` |
| Bottom | Text box | The two-crisis hook: earnings −72%/dividend −49% vs earnings −79%/dividend −4% |

---

### Page 2 — 155 Years

| Position | Visual | Fields |
|---|---|---|
| Left, large | Line chart | Axis `Dim_Year[Year]`; value `[Payout Ratio]`; add a **constant line** at the full-sample median |
| Right top | Clustered column | Axis `Dim_Era[Era]`; value `[Median Payout Ratio]`; conditional colour by `Dim_Era[Regime]` |
| Right bottom | Line chart | Axis `Dim_Year[Year]`; values `[Real Dividend]` and `[Real Earnings]`, **log scale** |
| Bottom | Matrix | Rows `Dim_Era[Era]`; values `[Median Payout Ratio]`, `[Median Dividend Yield]`, `[CAPE]`, `[Long Rate]`, `[Smoothing Ratio]`, `[Real Dividend CAGR]` |

Log scale on the real dividend/earnings chart is essential — over 155 years a linear axis compresses the first century into a flat line.

---

### Page 3 — The 1982 Break

*This is the analytical centrepiece. Give it the most design attention.*

| Position | Visual | Fields |
|---|---|---|
| Top, full width | Clustered column | Axis `Dim_Era[Era]`; value `[Speed of Adjustment]`; **colour by `Fact_Lintner[Regime]`** — teal pre-1982, gold post |
| Below, 3 cards | Card | `[Speed of Adjustment Pre 1982]`, `[Speed of Adjustment Post 1982]`, `[Adjustment Collapse Ratio]` |
| Left | Line chart | Source `Fact_Rolling`; axis `Year`; value `SmoothRatio`. Add a **shaded region** or vertical line at 1982 |
| Right | Table | `Dim_Era[Era]`, `[Speed of Adjustment]`, `[Lintner t stat]`, `[Lintner R2]`, `[Adjustment Half Life]`, `[Is Significant]` |
| Bottom | Text box | Rule 10b-18 explanation, and the honest caveat that no buyback series is available |

**Conditional formatting on the table:** `[Lintner t stat]` background — red below 2, green above. It makes the 2009–2023 row (t = 0.89) jump out.

The rolling chart matters more than it looks: it's your answer to "did you choose the eras to get this result?"

---

### Page 4 — Crises

| Position | Visual | Fields |
|---|---|---|
| Full width | Clustered column | Axis `Fact_Crises[Crisis]`; values `EarnDrawdown`, `DivDrawdown`, `PriceDrawdown` |
| Left | Table | `Crisis`, `Start`, `End`, `[Earnings Drawdown]`, `[Dividend Drawdown]`, `[Dividend Cushion]`, `[Crisis Verdict]` |
| Right | Card + text | `[Share of Shock Absorbed by Dividend]` in 48pt, filtered to the GFC |

Sort the crisis axis chronologically, not alphabetically — the widening gap over time is the whole point and alphabetical order destroys it.

---

### Page 5 — Who Still Pays

| Position | Visual | Fields |
|---|---|---|
| Left | Bar chart | Axis `Dim_Sector[Sector]`; value `[Payer Share]`; sorted descending |
| Right top | Clustered column | Axis `Dim_AgeBand[AgeBandKey]`; value `[Payer Share]`; line overlay `[Median Firm Yield]` |
| Right bottom | Card | `[Life Cycle Gradient]` and `[Life Cycle Verdict]` |
| Bottom | Table | `Dim_Company[Security]`, `Sector`, `Founded`, `[Median Firm Yield]`, `[Median Firm PE]`, `[Median Firm PB]`, `[Median Market Cap Bn]`, `Payer` |

Add a **slicer on `Dim_Company[PayerLabel]`** so the audience can flip between payers and non-payers live. Watching Information Technology dominate the non-payer list is more persuasive than any chart.

---

### Page 6 — Yield and Returns

| Position | Visual | Fields |
|---|---|---|
| Left, large | Scatter | Source `Fact_Predictive`; X `StartingDivYield`; Y `Fwd10yRealReturn`; play axis `YearKey` |
| Right | Card | `[Yield Return Correlation]` |
| Right | Text box | **The overlapping-windows caveat.** Put it on the page, not in the notes |

Turn on the **trend line** in the scatter's Analytics pane.

---

### Page 7 — Gulf Contrast

| Position | Visual | Fields |
|---|---|---|
| Left | Combo chart | Axis `Fact_Aramco[Year]`; column `PayoutOfFCF`; line `SP500PayoutNow` as a constant benchmark |
| Right top | Cards | `[Aramco Payout of FCF]`, `[Aramco Payout Range]`, `[Gulf vs US Gap]` |
| Right bottom | Text box | The ownership argument — 97.5% sovereign, can't sell to manufacture income, so the dividend does the work |

---

## 6. Finishing touches that carry marks

- **Bookmarks + buttons** across the top, one per section, so you navigate a narrative rather than hunting tabs
- **Tooltip page** (sized to *Tooltip*) with a small payout-over-time chart, set as the tooltip for the era matrix
- **Drill-through** page filtered by `Dim_Sector[Sector]` so right-clicking a sector bar jumps to its firm list
- **A limitations text box on page 3 and page 6.** Being visibly honest about the missing buyback series and the overlapping windows reads as rigour, and pre-empts the two questions most likely to be asked

---

## 7. Pre-flight checklist

- [ ] `Dim_Year` marked as a date table
- [ ] `Dim_Era` sorted by `EraSort`, `Dim_AgeBand` sorted by `Sort`
- [ ] Teal/gold regime convention consistent on every chart
- [ ] Crisis axis in chronological order
- [ ] No blank visuals when all slicers are cleared
- [ ] `[Smoothing Ratio]` returns a number at every slicer combination
- [ ] File → Options → Current file → **disable "Persistent filters"** so it opens in a known state
- [ ] Export to PDF once as a fallback for the day
