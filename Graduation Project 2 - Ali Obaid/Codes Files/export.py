"""Exports every analysis result to CSV + a JSON payload for the dashboard/deck/report."""
import json
import numpy as np
import pandas as pd
from engine import (load_shiller, load_cross_section, load_rates, era_table, decade_table,
                    lintner, crisis_table, predictive_regression, sector_table,
                    lifecycle_table, ERAS)

OUT = "/home/claude/dividend/output/"
import os
os.makedirs(OUT, exist_ok=True)

d = load_shiller()
m = load_cross_section()
rates = load_rates()

# ---------------------------------------------------------------- tables
eras = era_table(d)
decs = decade_table(d)
cris = crisis_table(d)
sect = sector_table(m)
life = lifecycle_table(m)
pr = predictive_regression(d)

common_target = float((d.groupby("Year").Dividend.mean() / d.groupby("Year").Earnings.mean()).median())
lin_full = lintner(d)
lin_pre = lintner(d[d.Year <= 1981], target=common_target)
lin_post = lintner(d[d.Year >= 1982], target=common_target)
lin_era = []
for name, a, b in ERAS:
    r = lintner(d[(d.Year >= a) & (d.Year <= b)])
    if r:
        lin_era.append(dict(Era=name, Start=a, End=b, c=r["c"], t=r["t"], r2=r["r2"],
                            n=r["n"], target=r["target"], halflife=r["halflife"]))
lin_era = pd.DataFrame(lin_era)

# annual series (for charts + Excel)
ann = d.groupby("Year").agg(
    Price=("SP500", "mean"), Dividend=("Dividend", "mean"), Earnings=("Earnings", "mean"),
    CPI=("CPI", "mean"), Rate10Y=("Rate10Y", "mean"), CAPE=("CAPE", "mean"),
    RealDiv=("RealDiv", "mean"), RealEarn=("RealEarn", "mean"),
    RealPrice=("RealPrice", "mean")).reset_index()
ann["Payout"] = ann.Dividend / ann.Earnings
ann["DivYield"] = ann.Dividend / ann.Price
ann["EarnYield"] = ann.Earnings / ann.Price
ann["PE"] = ann.Price / ann.Earnings
ann["DivGrowth"] = ann.Dividend.pct_change()
ann["EarnGrowth"] = ann.Earnings.pct_change()
ann["Era"] = ann.Year.map(lambda y: next((n for n, a, b in ERAS if a <= y <= b), None))

# rolling 20-year smoothing ratio - the structural break, visualised
roll = []
for y in range(1891, 2024):
    w = ann[(ann.Year > y - 20) & (ann.Year <= y)]
    dv, ev = w.DivGrowth.std(), w.EarnGrowth.std()
    pay = w.Payout.median()
    roll.append(dict(Year=y, SmoothRatio=(dv / ev if ev and ev > 0 else np.nan),
                     Payout=pay, DivYield=w.DivYield.median()))
roll = pd.DataFrame(roll)

# ---------------------------------------------------------------- CSVs
for name, t in [("annual_series", ann), ("by_era", eras), ("by_decade", decs),
                ("lintner_by_era", lin_era), ("crises", cris), ("sector_cross_section", sect),
                ("lifecycle", life), ("rolling_smoothing", roll),
                ("firm_level", m[["Symbol", "Security", "Sector", "SubIndustry", "Founded", "Age",
                                  "YearAdded", "Price", "PE", "PB", "DivYield", "EPS",
                                  "MarketCapBn", "Payer", "PayoutRatio"]])]:
    t.to_csv(OUT + name + ".csv", index=False)
d.to_csv(OUT + "shiller_monthly_processed.csv", index=False)

# ---------------------------------------------------------------- JSON payload
def cl(x):
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, (np.floating, float)):
        return None if (pd.isna(x) or np.isinf(x)) else round(float(x), 6)
    if isinstance(x, (np.bool_, bool)): return bool(x)
    return x

def recs(t):
    return [{k: cl(v) for k, v in r.items()} for _, r in t.iterrows()]

payload = dict(
    meta=dict(months=len(d), years=int(d.Year.max() - d.Year.min() + 1),
              start=str(d.Date.min().date()), end=str(d.Date.max().date()),
              firms=len(m), sectors=int(m.Sector.nunique()),
              observations=int(len(d) * 8 + len(m) * 12 + len(rates))),
    annual=recs(ann[["Year", "Price", "Dividend", "Earnings", "Payout", "DivYield", "CAPE",
                     "Rate10Y", "RealDiv", "RealEarn", "DivGrowth", "EarnGrowth", "Era"]]),
    eras=recs(eras), decades=recs(decs), crises=recs(cris),
    lintner_era=recs(lin_era), sectors=recs(sect), lifecycle=recs(life),
    rolling=recs(roll),
    firms=recs(m[["Symbol", "Security", "Sector", "Founded", "Age", "PE", "PB",
                  "DivYield", "MarketCapBn", "Payer"]]),
    predictive=dict(slope=cl(pr["slope"]), intercept=cl(pr["intercept"]), r2=cl(pr["r2"]),
                    corr=cl(pr["corr"]), n=int(pr["n"]), cape_r2=cl(pr["cape_r2"]),
                    scatter=[dict(y=cl(r.DivYield), r=cl(r.FwdReal), yr=int(r.Year))
                             for _, r in pr["data"].iloc[::6].iterrows()]),
    lintner=dict(full={k: cl(v) for k, v in lin_full.items()},
                 pre={k: cl(v) for k, v in lin_pre.items()},
                 post={k: cl(v) for k, v in lin_post.items()},
                 common_target=cl(common_target)),
    findings=dict(
        payout_then=cl(eras.iloc[0].Payout), payout_now=cl(eras.iloc[-1].Payout),
        yield_then=cl(eras.iloc[0].DivYield), yield_now=cl(eras.iloc[-1].DivYield),
        smooth_then=cl(eras.iloc[0].SmoothRatio), smooth_now=cl(eras.iloc[-1].SmoothRatio),
        c_pre=cl(np.mean([r["c"] for r in lin_era.to_dict("records") if r["End"] <= 1981])),
        c_post=cl(np.mean([r["c"] for r in lin_era.to_dict("records") if r["Start"] >= 1982])),
        halflife_pre=cl(lin_pre["halflife"]), halflife_post=cl(lin_post["halflife"]),
        gfc_earn=cl(cris[cris.Crisis == "Global financial crisis"].EarnDrawdown.iloc[0]),
        gfc_div=cl(cris[cris.Crisis == "Global financial crisis"].DivDrawdown.iloc[0]),
        dep_earn=cl(cris[cris.Crisis == "Great Depression"].EarnDrawdown.iloc[0]),
        dep_div=cl(cris[cris.Crisis == "Great Depression"].DivDrawdown.iloc[0]),
        payer_pct=cl(m.Payer.mean()), payers=int(m.Payer.sum()), nonpayers=int((~m.Payer).sum()),
        tech_payer=cl(sect[sect.Sector == "Information Technology"].PayerPct.iloc[0]),
        util_payer=cl(sect[sect.Sector == "Utilities"].PayerPct.iloc[0]),
        life_young=cl(life.iloc[0].PayerPct), life_old=cl(life[life.AgeBand == "100-150y"].PayerPct.iloc[0]),
        pred_r2=cl(pr["r2"]), cape_r2=cl(pr["cape_r2"]),
    ),
    # Gulf contrast - from the FY2019-FY2025 Aramco study
    aramco=dict(years=[2019, 2020, 2021, 2022, 2023, 2024, 2025],
                payout_fcf=[0.935, 1.531, 0.698, 0.505, 0.966, 1.456, 1.000],
                total_div=[73.2, 75.0, 75.0, 75.0, 97.8, 124.245, 85.453],
                fcf=[78.3, 49.0, 107.5, 148.5, 101.2, 85.333, 85.428],
                cum_payout=0.9243, state_share=0.975),
)
open(OUT + "payload.json", "w").write(json.dumps(payload))

print("exported to", OUT)
print(f"  monthly obs {len(d)} | annual {len(ann)} | firms {len(m)} | eras {len(eras)} | crises {len(cris)}")
print(f"  total real data points ~{payload['meta']['observations']:,}")
for f in sorted(os.listdir(OUT)):
    print("   ", f, f"{os.path.getsize(OUT+f)//1024}KB")
