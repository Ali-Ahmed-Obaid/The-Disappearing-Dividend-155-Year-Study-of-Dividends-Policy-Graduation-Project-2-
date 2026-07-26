"""Exports a Power BI star schema for the Disappearing Dividend project."""
import os, json
import numpy as np
import pandas as pd

O = "/home/claude/dividend/output/"
PB = "/home/claude/dividend/powerbi/"
os.makedirs(PB, exist_ok=True)

P = json.load(open(O + "payload.json"))
mon = pd.read_csv(O + "shiller_monthly_processed.csv")
ann = pd.read_csv(O + "annual_series.csv")
firms = pd.read_csv(O + "firm_level.csv")
roll = pd.read_csv(O + "rolling_smoothing.csv")

ERAS = [("1871-1900  Gilded Age", 1871, 1900), ("1901-1929  Pre-Crash", 1901, 1929),
        ("1930-1945  Depression & War", 1930, 1945), ("1946-1972  Post-war boom", 1946, 1972),
        ("1973-1981  Stagflation", 1973, 1981), ("1982-1999  Buyback era begins", 1982, 1999),
        ("2000-2008  Dot-com to GFC", 2000, 2008), ("2009-2023  Post-GFC", 2009, 2023)]

# ------------------------------------------------------------ DIMENSIONS
dim_year = pd.DataFrame({"Year": sorted(ann.Year.unique())})
dim_year["Decade"] = (dim_year.Year // 10) * 10
dim_year["DecadeLabel"] = dim_year.Decade.astype(str) + "s"
dim_year["Century"] = np.where(dim_year.Year < 1900, "19th",
                        np.where(dim_year.Year < 2000, "20th", "21st"))
dim_year["Era"] = dim_year.Year.map(lambda y: next((n for n, a, b in ERAS if a <= y <= b), "Other"))
dim_year["EraSort"] = dim_year.Year.map(lambda y: next((i for i, (n, a, b) in enumerate(ERAS) if a <= y <= b), 99))
dim_year["Regime"] = np.where(dim_year.Year <= 1981, "Pre-1982 (before Rule 10b-18)",
                              "Post-1982 (buyback era)")
dim_year["YearEndDate"] = pd.to_datetime(dim_year.Year.astype(str) + "-12-31")

dim_era = pd.DataFrame([{"Era": n, "EraSort": i, "StartYear": a, "EndYear": b,
                         "Regime": "Pre-1982" if b <= 1981 else "Post-1982",
                         "Years": b - a + 1} for i, (n, a, b) in enumerate(ERAS)])

dim_sector = firms.groupby("Sector").agg(
    Firms=("Symbol", "count"), Payers=("Payer", "sum")).reset_index()
dim_sector["SectorKey"] = dim_sector.Sector
dim_sector["PayerPct"] = dim_sector.Payers / dim_sector.Firms
dim_sector["PayerBand"] = pd.cut(dim_sector.PayerPct, [0, .7, .9, 1.01],
                                 labels=["Low (<70%)", "Medium (70-90%)", "High (>90%)"])

dim_company = firms[["Symbol", "Security", "Sector", "SubIndustry", "Founded", "Age",
                     "YearAdded", "Payer"]].copy()
dim_company["CompanyKey"] = dim_company.Symbol
dim_company["AgeBand"] = pd.cut(dim_company.Age, [0, 25, 50, 75, 100, 150, 300],
    labels=["<25y", "25-50y", "50-75y", "75-100y", "100-150y", "150y+"])
dim_company["PayerLabel"] = np.where(dim_company.Payer, "Pays a dividend", "Does not pay")

dim_ageband = pd.DataFrame(P["lifecycle"]).rename(columns={"AgeBand": "AgeBandKey"})
dim_ageband["Sort"] = range(len(dim_ageband))

# ------------------------------------------------------------ FACTS
fact_annual = ann.copy()
fact_annual["YearKey"] = fact_annual.Year
fact_annual = fact_annual[["YearKey", "Price", "Dividend", "Earnings", "Payout", "DivYield",
                           "EarnYield", "PE", "CAPE", "Rate10Y", "RealDiv", "RealEarn",
                           "RealPrice", "DivGrowth", "EarnGrowth"]]

fm = mon.copy()
fm["Date"] = pd.to_datetime(fm.Date)
fm["YearKey"] = fm.Year
fact_monthly = fm[["Date", "YearKey", "SP500", "Dividend", "Earnings", "CPI", "Rate10Y",
                   "CAPE", "RealPrice", "RealDiv", "RealEarn", "Payout", "DivYield", "PE",
                   "TRIndex", "RealTRIndex"]]

fact_firm = firms.copy()
fact_firm["CompanyKey"] = fact_firm.Symbol
fact_firm["SectorKey"] = fact_firm.Sector
fact_firm["AgeBandKey"] = pd.cut(fact_firm.Age, [0, 25, 50, 75, 100, 150, 300],
    labels=["<25y", "25-50y", "50-75y", "75-100y", "100-150y", "150y+"])
fact_firm = fact_firm[["CompanyKey", "SectorKey", "AgeBandKey", "Price", "PE", "PB",
                       "DivYield", "EPS", "MarketCapBn", "Payer", "PayoutRatio", "Age", "Founded"]]

fact_era = pd.DataFrame(P["eras"])
fact_era["EraSort"] = range(len(fact_era))
fact_lintner = pd.DataFrame(P["lintner_era"])
fact_lintner["EraSort"] = range(len(fact_lintner))
fact_lintner["Regime"] = np.where(fact_lintner.Start <= 1981, "Pre-1982", "Post-1982")

fact_crises = pd.DataFrame(P["crises"])
fact_crises["CrisisKey"] = fact_crises.Crisis
fact_crises["Century"] = np.where(fact_crises.Start < 1900, "19th",
                          np.where(fact_crises.Start < 2000, "20th", "21st"))

fact_rolling = roll.copy()
fact_rolling["YearKey"] = fact_rolling.Year

fact_predictive = pd.DataFrame(P["predictive"]["scatter"]).rename(
    columns={"y": "StartingDivYield", "r": "Fwd10yRealReturn", "yr": "YearKey"})

A = P["aramco"]
fact_aramco = pd.DataFrame({"Year": A["years"], "FreeCashFlowBn": A["fcf"],
    "DistributionsBn": A["total_div"], "PayoutOfFCF": A["payout_fcf"]})
fact_aramco["SP500PayoutNow"] = P["findings"]["payout_now"]
fact_aramco["SP500PayoutThen"] = P["findings"]["payout_then"]

# reference table for benchmark lines / cards
tbl_findings = pd.DataFrame([{"Metric": k, "Value": v} for k, v in P["findings"].items()])

TABLES = {
    "Dim_Year": dim_year, "Dim_Era": dim_era, "Dim_Sector": dim_sector,
    "Dim_Company": dim_company, "Dim_AgeBand": dim_ageband,
    "Fact_Annual": fact_annual, "Fact_Monthly": fact_monthly, "Fact_Firm": fact_firm,
    "Fact_Era": fact_era, "Fact_Lintner": fact_lintner, "Fact_Crises": fact_crises,
    "Fact_Rolling": fact_rolling, "Fact_Predictive": fact_predictive,
    "Fact_Aramco": fact_aramco, "Ref_Findings": tbl_findings,
}
for n, t in TABLES.items():
    t.to_csv(PB + n + ".csv", index=False, float_format="%.6f")

print("Power BI star schema written to", PB)
for n, t in TABLES.items():
    print(f"  {n:20s} {t.shape[0]:>5d} rows x {t.shape[1]:>2d} cols")
print(f"\n  total rows: {sum(t.shape[0] for t in TABLES.values()):,}")
