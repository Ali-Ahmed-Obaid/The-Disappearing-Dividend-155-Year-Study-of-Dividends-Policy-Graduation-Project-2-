"""
=====================================================================
 THE DISAPPEARING DIVIDEND
 155 years of US corporate payout policy  |  1871 - 2023
 Ali Ahmed Obaid (201933250) | Financial Policy | KFUPM
=====================================================================
 ALL DATA IS REAL. Sources:
   shiller_sp500.csv   Robert Shiller's long-run S&P 500 series, monthly
                       Jan-1871 to Jun-2023. Price, dividend, earnings,
                       CPI, 10-year rate, CAPE.
   sp500_constituents  Current S&P 500 members: GICS sector, date added,
                       year founded, CIK.
   sp500_financials    Current per-firm price, P/E, dividend yield, EPS,
                       market cap, EBITDA, P/S, P/B.
   us10y_monthly.csv   US 10-year Treasury constant maturity, monthly.
=====================================================================
"""
import numpy as np
import pandas as pd

D = "/home/claude/dividend/data/"


# ---------------------------------------------------------------- LOAD
def load_shiller():
    d = pd.read_csv(D + "shiller_sp500.csv")
    d["Date"] = pd.to_datetime(d["Date"])
    d = d.rename(columns={"Consumer Price Index": "CPI", "Long Interest Rate": "Rate10Y",
                          "Real Price": "RealPrice", "Real Dividend": "RealDiv",
                          "Real Earnings": "RealEarn", "PE10": "CAPE"})
    for c in ["Dividend", "Earnings", "CPI", "Rate10Y", "CAPE", "RealPrice", "RealDiv", "RealEarn"]:
        d[c] = d[c].replace(0, np.nan)
    d = d[d.Dividend.notna() & d.Earnings.notna()].copy()
    d["Year"] = d.Date.dt.year
    d["Payout"] = d.Dividend / d.Earnings
    d["DivYield"] = d.Dividend / d.SP500
    d["EarnYield"] = d.Earnings / d.SP500
    d["PE"] = d.SP500 / d.Earnings
    # total-return index: reinvest the monthly slice of the annualised dividend
    r = (d.SP500.pct_change() + (d.Dividend.shift(1) / 12) / d.SP500.shift(1)).fillna(0)
    d["TRIndex"] = (1 + r).cumprod()
    d["RealTRIndex"] = d.TRIndex / (d.CPI / d.CPI.iloc[0])
    return d.reset_index(drop=True)


def load_cross_section():
    c = pd.read_csv(D + "sp500_constituents.csv")
    f = pd.read_csv(D + "sp500_financials_snapshot.csv")
    c = c.rename(columns={"GICS Sector": "Sector", "GICS Sub-Industry": "SubIndustry",
                          "Date added": "DateAdded"})
    f = f.rename(columns={"Dividend Yield": "DivYield", "Price/Earnings": "PE",
                          "Earnings/Share": "EPS", "Market Cap": "MarketCap",
                          "Price/Sales": "PS", "Price/Book": "PB"})
    m = c.merge(f[["Symbol", "Price", "PE", "DivYield", "EPS", "MarketCap", "EBITDA", "PS", "PB"]],
                on="Symbol", how="inner")
    m["Founded"] = pd.to_numeric(m.Founded.astype(str).str.extract(r"(\d{4})")[0], errors="coerce")
    m["Age"] = 2026 - m.Founded
    m["YearAdded"] = pd.to_numeric(m.DateAdded.astype(str).str[:4], errors="coerce")
    m["Payer"] = m.DivYield > 0
    m["MarketCapBn"] = m.MarketCap / 1e9
    m["PayoutRatio"] = np.where(m.EPS > 0, m.DivYield * m.Price / m.EPS, np.nan)
    return m


def load_rates():
    r = pd.read_csv(D + "us10y_monthly.csv")
    r["Date"] = pd.to_datetime(r["Date"])
    return r.rename(columns={"Rate": "US10Y"})


# ---------------------------------------------------------------- ERAS
ERAS = [
    ("1871-1900  Gilded Age", 1871, 1900),
    ("1901-1929  Pre-Crash", 1901, 1929),
    ("1930-1945  Depression & War", 1930, 1945),
    ("1946-1972  Post-war boom", 1946, 1972),
    ("1973-1981  Stagflation", 1973, 1981),
    ("1982-1999  Buyback era begins", 1982, 1999),
    ("2000-2008  Dot-com to GFC", 2000, 2008),
    ("2009-2023  Post-GFC", 2009, 2023),
]


def era_of(y):
    for name, a, b in ERAS:
        if a <= y <= b:
            return name
    return None


# ---------------------------------------------------------------- ANALYSES
def decade_table(d):
    d = d.copy()
    d["Decade"] = (d.Year // 10) * 10
    g = d.groupby("Decade").agg(
        Payout=("Payout", "median"), DivYield=("DivYield", "median"),
        CAPE=("CAPE", "median"), Rate=("Rate10Y", "median"),
        RealDiv=("RealDiv", "median"), RealEarn=("RealEarn", "median"),
        Months=("Payout", "size")).reset_index()
    g["PayoutStd"] = d.groupby("Decade").Payout.std().values
    return g


def era_table(d):
    d = d.copy()
    d["Era"] = d.Year.map(era_of)
    rows = []
    for name, a, b in ERAS:
        s = d[(d.Year >= a) & (d.Year <= b)]
        if not len(s):
            continue
        ann = s.groupby("Year").agg(Div=("Dividend", "mean"), Earn=("Earnings", "mean"),
                                    RD=("RealDiv", "mean"), RE=("RealEarn", "mean"))
        dd, de = ann.Div.pct_change().dropna(), ann.Earn.pct_change().dropna()
        rows.append(dict(
            Era=name, Start=a, End=b, Months=len(s),
            Payout=s.Payout.median(), DivYield=s.DivYield.median(),
            CAPE=s.CAPE.median(), Rate=s.Rate10Y.median(),
            DivGrowth=dd.mean(), EarnGrowth=de.mean(),
            DivVol=dd.std(), EarnVol=de.std(),
            SmoothRatio=(dd.std() / de.std() if de.std() else np.nan),
            RealDivCAGR=((ann.RD.iloc[-1] / ann.RD.iloc[0]) ** (1 / max(len(ann) - 1, 1)) - 1),
            RealEarnCAGR=((ann.RE.iloc[-1] / ann.RE.iloc[0]) ** (1 / max(len(ann) - 1, 1)) - 1)))
    return pd.DataFrame(rows)


def lintner(d, target=None):
    """Lintner partial adjustment on ANNUAL data:
         dD_t = a + c * (r * E_t - D_(t-1)) + e
       c is the speed of adjustment; r the long-run target payout."""
    a = d.groupby("Year").agg(D=("Dividend", "mean"), E=("Earnings", "mean")).dropna()
    a = a[a.E > 0]
    r = target if target else (a.D / a.E).median()
    a["Dlag"] = a.D.shift(1)
    a["dD"] = a.D - a.Dlag
    a["gap"] = r * a.E - a.Dlag
    a = a.dropna()
    if len(a) < 6:
        return None
    x, y = a.gap.values, a.dD.values
    n = len(x)
    sx, sy = x.sum(), y.sum()
    sxx, sxy = (x * x).sum(), (x * y).sum()
    den = n * sxx - sx * sx
    c = (n * sxy - sx * sy) / den
    inter = (sy - c * sx) / n
    yhat = inter + c * x
    ssr = ((y - yhat) ** 2).sum()
    sst = ((y - y.mean()) ** 2).sum()
    r2 = 1 - ssr / sst if sst else np.nan
    se_c = np.sqrt(ssr / (n - 2) / (sxx - sx * sx / n)) if n > 2 else np.nan
    return dict(c=c, intercept=inter, r2=r2, se=se_c, t=c / se_c if se_c else np.nan,
                n=n, target=r, halflife=(np.log(0.5) / np.log(1 - c) if 0 < c < 1 else np.nan))


CRISES = [
    ("Panic of 1873", 1873, 1879), ("Panic of 1893", 1893, 1897),
    ("Panic of 1907", 1907, 1908), ("Great Depression", 1929, 1933),
    ("1937 recession", 1937, 1938), ("Oil shock / stagflation", 1973, 1975),
    ("Dot-com bust", 2000, 2002), ("Global financial crisis", 2007, 2009),
    ("COVID-19", 2020, 2020),
]


def crisis_table(d):
    a = d.groupby("Year").agg(D=("Dividend", "mean"), E=("Earnings", "mean"),
                              P=("SP500", "mean"), RD=("RealDiv", "mean"),
                              RE=("RealEarn", "mean")).dropna()
    rows = []
    for name, s, e in CRISES:
        w = a[(a.index >= s - 1) & (a.index <= e + 1)]
        if len(w) < 2:
            continue
        pk = a.index[a.index <= s].max()
        base = a.loc[pk]
        tr = a[(a.index >= s) & (a.index <= e)]
        rows.append(dict(
            Crisis=name, Start=s, End=e,
            DivDrawdown=tr.D.min() / base.D - 1,
            EarnDrawdown=tr.E.min() / base.E - 1,
            PriceDrawdown=tr.P.min() / base.P - 1,
            RealDivDrawdown=tr.RD.min() / base.RD - 1,
            Cushion=(tr.E.min() / base.E - 1) - (tr.D.min() / base.D - 1)))
    return pd.DataFrame(rows)


def predictive_regression(d, horizon_years=10):
    """Classic Campbell-Shiller: does the dividend yield predict future real returns?"""
    d = d.copy().reset_index(drop=True)
    h = horizon_years * 12
    d["FwdReal"] = (d.RealTRIndex.shift(-h) / d.RealTRIndex) ** (1 / horizon_years) - 1
    s = d[["Date", "Year", "DivYield", "CAPE", "FwdReal"]].dropna()
    x, y = s.DivYield.values, s.FwdReal.values
    n = len(x)
    b = np.polyfit(x, y, 1)
    yhat = np.polyval(b, x)
    r2 = 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    xc, yc = np.polyfit(1 / s.CAPE.values, y, 1), None
    yh2 = np.polyval(xc, 1 / s.CAPE.values)
    r2c = 1 - ((y - yh2) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return dict(slope=b[0], intercept=b[1], r2=r2, n=n,
                cape_slope=xc[0], cape_intercept=xc[1], cape_r2=r2c,
                corr=np.corrcoef(x, y)[0, 1], data=s)


def sector_table(m):
    g = m.groupby("Sector").agg(
        Firms=("Symbol", "count"), Payers=("Payer", "sum"),
        MedYield=("DivYield", lambda s: s[s > 0].median()),
        MedPE=("PE", "median"), MedPB=("PB", "median"),
        MedAge=("Age", "median"), MedCapBn=("MarketCapBn", "median"),
        TotalCapBn=("MarketCapBn", "sum")).reset_index()
    g["PayerPct"] = g.Payers / g.Firms
    return g.sort_values("PayerPct", ascending=False)


def lifecycle_table(m):
    """Life-cycle theory: older, more mature firms should be more likely to pay."""
    b = pd.cut(m.Age, [0, 25, 50, 75, 100, 150, 300],
               labels=["<25y", "25-50y", "50-75y", "75-100y", "100-150y", "150y+"])
    g = m.groupby(b, observed=True).agg(
        Firms=("Symbol", "count"), Payers=("Payer", "sum"),
        MedYield=("DivYield", lambda s: s[s > 0].median()),
        MedCapBn=("MarketCapBn", "median"), MedPB=("PB", "median")).reset_index()
    g["PayerPct"] = g.Payers / g.Firms
    g = g.rename(columns={g.columns[0]: "AgeBand"})
    return g


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    d = load_shiller()
    m = load_cross_section()
    print(f"Shiller panel: {len(d)} monthly observations, {d.Year.min()}-{d.Year.max()}")
    print(f"Cross-section: {len(m)} firms, {m.Sector.nunique()} GICS sectors\n")

    print("=== PAYOUT BY ERA (real) ===")
    e = era_table(d)
    print(e[["Era", "Months", "Payout", "DivYield", "CAPE", "Rate", "SmoothRatio",
             "RealDivCAGR", "RealEarnCAGR"]].round(3).to_string(index=False))

    print("\n=== LINTNER, FULL SAMPLE 1871-2023 ===")
    L = lintner(d)
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in L.items()})

    print("\n=== LINTNER BY ERA ===")
    for name, a, b in ERAS:
        s = d[(d.Year >= a) & (d.Year <= b)]
        r = lintner(s)
        if r:
            print(f"  {name:32s} c={r['c']:6.3f}  t={r['t']:6.2f}  R2={r['r2']:5.3f}  n={r['n']:3d}")

    print("\n=== CRISIS BEHAVIOUR ===")
    print(crisis_table(d).round(3).to_string(index=False))

    print("\n=== DIVIDEND YIELD PREDICTS 10-YEAR REAL RETURNS ===")
    pr = predictive_regression(d)
    print(f"  slope {pr['slope']:.3f}  R2 {pr['r2']:.3f}  corr {pr['corr']:.3f}  n {pr['n']}")
    print(f"  CAPE (1/CAPE) R2 {pr['cape_r2']:.3f}")

    print("\n=== MODERN CROSS-SECTION BY SECTOR ===")
    print(sector_table(m).round(3).to_string(index=False))

    print("\n=== LIFE-CYCLE: firm age vs dividend policy ===")
    print(lifecycle_table(m).round(3).to_string(index=False))
