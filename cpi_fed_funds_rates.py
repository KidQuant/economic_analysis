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
