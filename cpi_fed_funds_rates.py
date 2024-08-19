# %%
import pandas as pd
import numpy as np
import matplotlib.ticker as mtick
import pandas_datareader.data as web
import pandas.tseries.offsets as BDay
from dateutil.relativedelta import relativedelta
from datetime import date

from pricing import curves

# %%
report_start = date.fromisoformat("1969-01-01")
report_end = date.today()


# %%
fred_cpi_ffr = web.get_data_fred(
    ["CPIAUCSL", "FEDFUNDS", "GS10", "GS3M", "FII10"],
    start=report_start,
    end=report_end,
)

real_gdp = web.get_data_fred("GDPC1", start=report_start, end=report_end)

# %%

# Since CPIAUCSL is indexed to 1982-1984=100, we need to convert it to annual percentage changes
fred_cpi_ffr.update(fred_cpi_ffr.CPIAUCSL.pct_change(12, fill_method="bfill") * 100)

# For real GDP I translate the growth over one quarter into annual rate to be consistent with
# how the BEA does it.
real_gdp_quarterly = (real_gdp / real_gdp.shift(1)).pow(4) - 1

# If instead you want to calculate GDP growth over the whole year, the correct way to do that is
real_gdp = real_gdp.rolling(4).mean().pct_change(4, fill_method="bfill").loc["1970":]

fred_cpi_ffr = fred_cpi_ffr.loc["1970":]
fred_cpi_ffr.rename(
    columns={
        "CPIAUCSL": "Annual seasonaly adjusted CPI",
        "FEDFUNDS": "Federal Funds Effective Rate",
        "GS10": "10y Treasury Yield",
        "GS3M": "3m Treasury Yield",
        "FII10": "10y TIPS Yield",
    },
    inplace=True,
)
real_gdp.rename(columns={"GDPC1": "Real GDP"}, inplace=True)
real_gdp["Real GDP over quarter at annual rate"] = real_gdp_quarterly
fred_cpi_ffr /= 100.0
pd.options.display.float_format = "{:.4%}".format
pd.options.display.max_rows = 20
fred_cpi_ffr.loc["2020":]

# %%
ax = fred_cpi_ffr.iloc[:, :-2].plot(
    figsize=(20, 10),
    grid=True,
    title="US annaul CPI, Fed funds rate, and 10y Treasury Yield",
    xticks=fred_cpi_ffr.index[::24],
    xlabel="",
    rot=45,
    yticks=np.arange(-0.25, 0.2, 0.025),
)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, fred_cpi_ffr.index[::24])))

# %%
from_date = date(2020, 1, 1)
cpi = web.get_data_fred("CPIAUCSL", start=report_start, end=report_end)
cpi_monthly = (
    cpi.pct_change(fill_method="bfill")
    .loc[from_date:, "CPIAUCSL"]
    .rename("CPI Change over Prev Month")
)

cpi_annual = (
    ((cpi / cpi.shift(1)).pow(12) - 1)
    .loc[from_date:, "CPIAUCSL"]
    .rename("CPI Change over Prev Month at Annual Rate")
)

cpi_quarterly = (
    ((cpi / cpi.shift(3)).pow(4) - 1)
    .loc[from_date:, "CPIAUCSL"]
    .rename("CPI Change over Prev 3 Months at Annual Rate")
)

# %%
cpi_df = pd.concat(
    [fred_cpi_ffr.loc[from_date:].iloc[:, 0], cpi_quarterly, cpi_annual], axis=1
)
cpi_df

#  %%
import seaborn as sns

cm = sns.color_palette("Blues", as_cmap=True)
IDX_FORMAT = "{:%Y-%m}"


# %%
# real_gdp.loc['2020']
cpi_df = cpi_df.loc["2020":, cpi_df.columns[0:2]]
cpi_df.tail(18).style.format_index(IDX_FORMAT).format("{:.2%}").set_properties(
    subset=cpi_df.columns, **{"width": "200px"}
).set_table_styles(
    [{"selector": "th", "props": "text-align: right; width: 100px"}]
).background_gradient(
    cmap=cm
)

# %%

# real_gdp.loc['2020':]
real_gdp.tail(18).style.format_index(IDX_FORMAT).format("{:.2%}").set_properties(
    subset=real_gdp.columns, **{"width": "200px"}
).set_table_styles(
    [{"selector": "th", "props": "text-align: right; width: 100px"}]
).background_gradient(
    cmap=cm
)

# %%
ax = real_gdp.iloc[:, 0].plot(
    figsize=(20, 10),
    grid=True,
    title="US Real GDP growth (annual rate)",
    xticks=real_gdp.index[::6],
    xlabel="",
    rot=45,
    yticks=np.arange(-0.05, 0.125, 0.025),
)
ax.axhline(y=0, lw=2, c="k")
ax.axhline(
    y=real_gdp.iloc[:, 0].mean(),
    lw=2,
    ls="--",
    c="red",
    label="Mean level of annual growth",
)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
ax2 = ax.twiny()
real_gdp.iloc[:, 0].plot.bar(ax=ax2, xlabel="", legend=False)
ax2.xaxis.set_major_locator(mtick.NullLocator())
ax.legend()
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, real_gdp.index[::6])))

# %%
print(
    f"Mean level of annual GDP growth since {real_gdp.index[0]:%Y-%m-%d}: {real_gdp.iloc[:, 0].mean():.2%}"
)

# %%

df = pd.concat([real_gdp.iloc[:, 0], fred_cpi_ffr.resample("qs").mean()], axis=1)
df.loc["1981":]

# %%

ax = df.iloc[:, -3].plot(
    figsize=(20, 10),
    grid=True,
    title="Annual CPI and Real GDP vs 10y Treasury Yield",
    xticks=df.index[::4],
    yticks=np.arange(-0.075, 0.2, 0.025),
    xlabel="",
    rot=45,
    linestyle="--",
    color="k",
)

ax2 = ax.twiny()
df.iloc[:, [0, 1]].plot.bar(ax=ax2, xlabel="", stacked=True)
ax.legend(loc="upper center")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
ax2.xaxis.set_major_locator(mtick.NullLocator())
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, df.index[::4])))

# %%

df = df.loc[: real_gdp.last_valid_index()]  # Truncate based on last valid GDP value
print(
    "Gap between intrinsic (GDP+CPI) and actual (10y Treasury) riskfree rates in quarter starting in {:%Y-%m}: {:.2%}\n"
    "Compared with: {:.2%} one quarter earlier\n".format(
        df.index[-1].date(),
        df.iloc[-1, 0] + df.iloc[-1, 1] - df.iloc[-1, 3],
        df.iloc[-2, 0] + df.iloc[-2, 1] - df.iloc[-2, 3],
    )
)

print(
    "Gap between intrinsic (GDP+CPI) and actual (3m Treasury) riskfree rates in quarter starting in {:%Y-%m}: {:.2%}\n"
    "Compared with: {:.2%} one quarter earlier\n".format(
        df.index[-1].date(),
        df.iloc[-1, 0] + df.iloc[-1, 1] - df.iloc[-1, 4],
        df.iloc[-2, 0] + df.iloc[-2, 1] - df.iloc[-2, 4],
    )
)

from_dt = date(1997, 1, 1)
# from_dt = df.index[0]
means = df.loc[from_dt:].mean()

print(
    "Average gap between intrinsic (GDP+CPI) and actual (10y Treasury) riskfree rates starting from {:%Y-%m}: {:.2%}".format(
        from_dt, means.iloc[0] + means.iloc[1] - means.iloc[3]
    )
)
print(
    "Average gap between intrinsic (GDP+CPI) and actual (3m Treasury) riskfree rates starting from {:%Y-%m}: {:.2%}".format(
        from_dt, means.iloc[0] + means.iloc[1] - means.iloc[4]
    )
)
# %%

df_gdp_tips = df.iloc[:, [0, -1]]
df_gdp_tips = df_gdp_tips.loc[df_gdp_tips.iloc[:, -1].first_valid_index() :]
ax = df_gdp_tips.iloc[:, -1].plot(
    figsize=(20, 10),
    grid=True,
    title="Real GDP vs 10y Real Yield (TIPS)",
    linewidth=2,
    xticks=df_gdp_tips.index[::2],
    yticks=np.arange(-0.075, 0.2, 0.025),
    xlabel="",
    rot=45,
    linestyle="--",
    color="k",
)
ax2 = ax.twiny()
df_gdp_tips.iloc[:, 0].plot.bar(ax=ax2, xlabel="", stacked=True)
ax.legend(loc="upper left")
ax2.legend(loc="upper right")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
ax2.xaxis.set_major_locator(mtick.NullLocator())
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, df_gdp_tips.index[::2])))


# %%

df_gdp_tips = df_gdp_tips.loc[: real_gdp.last_valid_index()]
print(
    "Gap between intrinsic GDP and actual 10y Real Riskfree Rate in quarter starting in {:%Y-%m}: {:.2%}\n"
    "Compared with: {:.2%} one quarter earlier\n".format(
        df_gdp_tips.index[-1].date(),
        df_gdp_tips.iloc[-1, 0] - df.iloc[-1, -1],
        df.iloc[-2, 0] - df.iloc[-2, -1],
    )
)
# %%

report_start = date.fromisoformat("2012-01-01")

# Treasury yield curve
data = web.get_data_fred(
    ["FEDFUNDS", "GS1", "GS2", "GS3", "GS5", "GS7", "GS10", "GS20", "GS30"],
    report_start,
    report_end,
)
data.dropna(inplace=True)

# The following data series aare only provided with daily frequences, hence we need to downsample them
# by taking their mean value over a given month and rounding to two decimal points (that's how values
# in series with monthly frequencies aaare calculated)
data2 = web.get_data_fred(["DGS1MO", "DGS3MO", "DGS6MO"], report_start, report_end)
data2 = data2.resample("MS").mean().round(2)

data = pd.concat([data, data2], axis=1).dropna()

# Rearranging columns
data = data[
    [
        "FEDFUNDS",
        "DGS1MO",
        "DGS3MO",
        "DGS6MO",
        "FEDFUNDS",
        "GS1",
        "GS2",
        "GS3",
        "GS5",
        "GS7",
        "GS10",
        "GS30",
    ]
]

# Renaming to reflect quarterly frequencies in the columns that used to have monthly frequencies
data.rename(
    columns={"DGS1MO": "GS1MO", "DGS3MO": "GS3MO", "DGS6MO": "GS6MO"}, inplace=True
)

data /= 100.0

# Converting the Fed Funds Rate to actual/actual
leap_year_cond = data.FEDFUNDS.index.year % 4 == 0 & (
    (data.FEDFUNDS.index.year % 100 != 0) | (data.FEDFUNDS.index.year % 400 == 0)
)
data.FEDFUNDS[leap_year_cond] *= 366.0 / 360
data.FEDFUNDS[np.invert(leap_year_cond)] *= 365.0 / 360

# Convertinng all CMT Yields to APY
data.iloc[:, 1:] = (data.iloc[:, 1:] / 2 + 1) ** 2 - 1

data

# %%

# Inflation expectation as givenn by breakeven inflation rates
data_infl_brk_even = web.get_data_fred(
    ["T5YIEM", "T7YIEM", "T10YIEM", "T20YIEM", "T30YIEM"], report_start, report_end
)
data_infl_brk_even.dropna(inplace=True)

cpi = fred_cpi_ffr[["Annual seasonaly adjusted CPI"]].loc["2012":]

# Expected inflation as calculated by the Federal Reserve Bank of Cleveland based on Inflation swap data,
# Treasury Yields, current CPI, Blue Chip forecast of CPI
data_infl = web.get_data_fred(
    ["EXPINF" + str(i) + "YR" for i in range(1, 31)], report_start, report_end
).shift(-1)

# Converting to decimal fractions, i.e. 1% is 0.01
data_infl_brk_even /= 100.0
data_infl /= 100.0

# Adding CPI and The Federal Reserve Bank of Cleveland 1 Year Inflation Expectation
data_infl = pd.concat([cpi, data_infl], axis=1).dropna()
data_infl_brk_even = pd.concat([cpi, data_infl_brk_even], axis=1)

# data_infl_brk_even.fillna(method='ffill', inplace=True
data_infl_brk_even
