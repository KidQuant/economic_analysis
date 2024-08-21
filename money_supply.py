# %%
import pandas as pd
import numpy as np
import matplotlib.ticker as mtick
import pandas_datareader.data as web
from datetime import date

# %%
report_start = date.fromisoformat("2008-10-01")
report_end = date.today()

# %%
nom_2_real_conv_factors = web.get_data_fred(
    "CPIAUCSL", start=report_start, end=report_end
)
nom_2_real_conv_factors["conv_factor"] = (
    nom_2_real_conv_factors.CPIAUCSL.iloc[-1] / nom_2_real_conv_factors.CPIAUCSL
)

# Convert into pandas.Series
nom_2_real_conv_factors = nom_2_real_conv_factors.conv_factor
# %%
report_start = date(2020, month=5, day=1)
# %%
m2_components = web.get_data_fred(
    ["MBCURRCIR", "M1NS", "M2NS"], start=report_start, end=report_end
)

m2_total = m2_components.M2NS.copy()
m2_total.rename("M2 Total", inplace=True)

# Converting into billions of USD
m2_components.MBCURRCIR /= 1000.0

# Subtracting smaller money aggregates from larger ones so that we have only additional parts
# contributed by each of the larger aggregates left
m2_components.M2NS -= m2_components.M1NS
m2_components.M1NS -= m2_components.MBCURRCIR

# %%
M2_COMPOSITION_TITLE = "Composition of US M2 Money Suppy"
REALM2_COMPOSITION_TITLE = "Composition of US Real M2 Money Supply"
IN_USD_FORMATTER = " in {:%Y-%m} USD"
LEFT_Y_AXIS_LABEL = "Billions of USD"
m2_components.rename(
    columns={
        "MBCURRICIR": "MB Currency in Circulation",
        "M1NS": "M1 Add-on",
        "M2NS": "M2 Add-on",
    },
    inplace=True,
)
pd.options.display.float_format = None
pd.concat([m2_total, m2_components], axis=1).tail(2)

# %%

# Convert from nominal into real money supply
m2real_total = (m2_total * nom_2_real_conv_factors).dropna()
m2real_components = m2_components.copy()
m2real_components = m2real_components.multiply(nom_2_real_conv_factors, axis=0).dropna()

m2real_total.rename("Real M2 Total", inplace=True)
m2real_components.rename(
    columns={
        "MB Currency in Circulation": "Real MB Currency in Circulation",
        "M1 Add-ons": "Real M1 Add-ons",
        "M2 Add-ons": "Real M2 Add-ons",
    },
    inplace=True,
)

pd.concat([m2real_total, m2real_components], axis=1).tail(18)

# %%

ax = m2_components.plot.area(
    figsize=(20, 10),
    grid=True,
    title=M2_COMPOSITION_TITLE,
    xticks=m2_components.index,
    xlabel="",
    rot=45,
    ylabel=LEFT_Y_AXIS_LABEL,
    yticks=np.arange(0, 25e3, 2.5e3),
)
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, m2_components.index)))

# %%

idxmax = m2_total.idxmax()
print(
    "Nominal M2 money supply maximum of {:>8.2f}bn reached in month {:%Y-%m}".format(
        m2_total.loc[idxmax], idxmax
    )
)
print(
    "Nominal M2 money supply shrank by  {:>8.2f}bn since (as of month {:%Y-%m})".format(
        m2_total.iloc[-1] - m2_total.loc[idxmax], m2_total.index[-1]
    )
)
print(
    "Nominal M2 money supply changed by  {:>8.2f}bn since {:%Y-%m} to {:.2f}bn".format(
        m2_total.iloc[-1] - m2_total.iloc[-2], m2_total.index[-2], m2_total.iloc[-1]
    )
)

m2_components.iloc[-1, :] - m2_components.iloc[-2, :]
# %%

# Converting to percentage by dividing by total M2 Money Supply
# Dividing by the total M2 Money Supply
m2_components_pct = m2_components.divide(m2_total, axis=0)
m2_components_pct *= 100

ax = m2_components_pct.plot.area(
    figsize=(20, 10),
    grid=True,
    title=M2_COMPOSITION_TITLE,
    xticks=m2_components_pct.index,
    xlabel="",
    rot=45,
    yticks=np.arange(0, 101, 5),
)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, m2_components_pct.index)))

# %%

m2_components_speed = (m2_components - m2_components.shift(1)).dropna()

# Converting to annual percentage changes (changes from the corresponding quarter a year ago)
m2_annual_rate = pd.concat([m2_total, m2_components], axis=1).pct_change(12)
m2_annual_rate = m2_annual_rate.loc["2021-05":]

# %%

ax = m2_annual_rate.iloc[:, :1].plot(
    figsize=(20, 10),
    grid=True,
    title="Main Components of US M2 Money Supply, Annual Percentage Changes",
    xticks=m2_annual_rate.index,
    xlabel="",
    rot=45,
    ylim=(-0.3, 0.35),
    yticks=np.arange(-0.30, 0.31, 0.05),
    linewidth=3,
)
m2_annual_rate.iloc[:, 1:].plot(
    ax=ax, grid=True, xticks=m2_annual_rate.index, xlabel="", rot=45, linewidth=1
)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
ax.axhline(y=0, lw=2, c="k")
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, m2_annual_rate.index)))

# %%

pd.options.display.float_format = lambda x: (
    "{:.3%}".format(x) if x < 100 else "{:,.0f}bn".format(x)
)
m2_annual_rate.tail(12)

# %%

M2_COMPONENTS_SPEED = (
    "Speed of changes in US M2 Money Supply in Billions of USD per month"
)
M2_COMPONENTS_CHANGES = "Changes in Components of US M2 Money Supply in Billions of USD"
M2REAL_COMPONENTS_SPEED = (
    "Speed of changes in US Real M2 Money Supply in Billions of USD per month"
)
M2REAL_COMPONENTS_CHANGES = (
    "Changes in Components of US Real M2 Money Supply in Billions of USD"
)
LEFT_Y_AXIS_LABEL = "Billions of USD"

ax = m2_components_speed.iloc[:, :].plot.bar(
    figsize=(20, 10), grid=True, xlabel="", rot=45, ylabel=LEFT_Y_AXIS_LABEL
)

_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, m2_components_speed.index)))

# %%

# In months
periods = [12, 18]

# If you want to include currency in circulation, use iloc[-1] in the expression below
m2_df_comp_changes = pd.DataFrame(
    [
        (m2_components - m2real_components.shift(period)).iloc[-1, 1:]
        for period in periods
    ],
    index=["Over past {:d} month".format(period) for period in periods],
)

ax = m2_df_comp_changes.plot.bar(
    figsize=(20, 10),
    grid=True,
    title=M2_COMPONENTS_CHANGES,
    stacked=True,
    rot=45,
    ylabel=LEFT_Y_AXIS_LABEL,
)
ax.get_legend().remove()
for c in ax.containers:
    ax.bar_label(c, fmt=c.get_label() + ": {:+,.0f}bn", label_type="center")

# %%

m2real_components_speed = (m2real_components - m2real_components.shift(1)).dropna()

# Converting to annual percentage change
m2real_annual_rate = pd.concat([m2real_total, m2real_components], axis=1).pct_change(12)
m2real_annual_rate = m2real_annual_rate.loc["2021-05":]

ax = m2real_annual_rate.iloc[:, :1].plot(
    figsize=(20, 10),
    grid=True,
    title="Main Components of US Real M2 Money Supply, Annual Percentage Changes",
    xticks=m2real_annual_rate.index,
    xlabel="",
    rot=45,
    ylim=(-0.3, 0.51),
    yticks=np.arange(-0.3, 0.51, 0.05),
    linewidth=3,
)
m2real_annual_rate.iloc[:, :1].plot(
    ax=ax, grid=True, xticks=m2_annual_rate.index, xlabel="", rot=45, linewidth=1
)
m2real_annual_rate.iloc[:, 1:].plot(
    ax=ax, grid=True, xticks=m2real_annual_rate.index, xlabel="", rot=45, linewidth=1
)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
ax.axhline(y=0, lw=2, c="k")
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, m2real_annual_rate.index)))

# %%

m2real_annual_rate.tail(12)

# %%

ax = m2_components_speed.iloc[:, :].plot.bar(
    figsize=(20, 10),
    grid=True,
    title=M2_COMPONENTS_SPEED,
    xlabel="",
    rot=45,
    ylabel=LEFT_Y_AXIS_LABEL,
)
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, m2_components_speed.index)))
# %%

# If you want include currency in circulation, use iloc[-1] in the expression below
m2real_df_comp_change = pd.DataFrame(
    [
        (m2real_components - m2real_components.shift(period)).iloc[-1, :1]
        for period in periods
    ],
    index=["Over past {:d} month".format(period) for period in periods],
)

ax = m2_df_comp_changes.plot.bar(
    figsize=(20, 10),
    grid=True,
    title=M2REAL_COMPONENTS_CHANGES,
    stacked=True,
    rot=45,
    ylabel=LEFT_Y_AXIS_LABEL,
)
ax.get_legend().remove()
for c in ax.containers:
    ax.bar_label(c, fmt=c.get_label() + ": {:+,.0f}bn", label_type="center")
# %%

report_start = date(2008, month=10, day=1)
mbase_reserves = web.get_data_fred(
    ["BOGMBBM", "GS1M"], start=report_start, end=report_end
)

# Converting reserve balances into billions of USD
mbase_reserves.BOGMBBM /= 1000.0

# Converting 1-month treasury yields into percentage points
mbase_reserves.GS1M /= 100.0

iorr = (
    web.get_data_fred("IORR", start=report_start, end=report_end).resample("MS").mean()
    / 100.0
)
iorb = (
    web.get_data_fred("IORB", start=report_start, end=report_end).resample("MS").mean()
    / 100.0
)
iorb = pd.concat([iorr.IORR, iorb.IORB])

# %%

# Approximate the latest value of Reservvev Balances
reserve_balances = web.get_data_fred(
    ["TERMT", "WLODLL"], start=report_start, end=report_end
).asfreq("W-Wed")
reserve_balances = reserve_balances.sum(axis=1).resample("MS").mean() / 1000.0
reserve_balances.rename("BOGMBBM", inplace=True)
idx = reserve_balances.index.difference(mbase_reserves.BOGMBBM.dropna().index)

# Approximate the latest value of 1-month treasury securities
latest_1m_tr_yield = (
    web.get_data_fred("DGS1MO", start=report_start, end=report_end).DGS1MO / 100.0
)
latest_1m_tr_yield = latest_1m_tr_yield.resample("MS").mean()
latest_1m_tr_yield.rename("GS1M", inplace=True)

# First update the missing values in mbase_reservves dataframe
mbase_reserves.update(
    pd.concat([reserve_balances[idx], latest_1m_tr_yield[idx]], axis=1)
)

# Now append the missing row if any
idx = reserve_balances.index.difference(mbase_reserves.index)
mbase_reserves = pd.concat(
    [
        mbase_reserves,
        pd.concat([reserve_balances[idx], latest_1m_tr_yield[idx]], axis=1),
    ]
)

# %%

# Upsampling to monthly frequencies to match the frequency of S&P 500 metrics
gdp = (
    web.get_data_fred("GDP", start=report_start, end=report_end)
    .GDP.resample("MS")
    .ffill()
)
missing_months = mbase_reserves.index.difference(gdp.index)
gdp = pd.concat([gdp, pd.Series(np.nan, index=missing_months)]).sort_index()


reserves_to_gdp = mbase_reserves.BOGMBBM / gdp

# %%

irt_reserves = pd.concat(
    [
        mbase_reserves.iloc[:, 0:],
        reserves_to_gdp,
        iorb,
        iorb - mbase_reserves.iloc[:, 1],
    ],
    axis=1,
)
irt_reserves.rename(
    columns={
        "BOGMBBM": "MB Reserve Balances",
        0: "MB Reserves to GDP",
        1: "Interest Rate on Reserves Balances",
        2: "Interest on Reserve Balance-1m Treasury yield",
    },
    inplace=True,
)
irt_reserves

# %%

LEFT_Y_AXIS_LABEL = "Billions of USD"
RIGHT_Y_AXIS_LABEL = "Reserves to GDP"
RESERVE_REQ_ABOLISH_DATE = "2020-04-01"
SLR_REINTRODUCTION_DATE = "2021-04-01"
QUANTITATIVE_TIGHTENING_DATE = "2022-06-01"
# ax = irt_reserves.iloc[:,[0,2]].plot(figsize=(20,10), grid=True,
ax = irt_reserves.iloc[:, :1].plot(
    figsize=(20, 10),
    grid=True,
    title="Monetary Base: Reserve Balances and their ratio to GDP",
    ylabel=LEFT_Y_AXIS_LABEL,
    xticks=irt_reserves.index[::6],
    xlabel="",
    rot=45,
    linewidth=2,
    yticks=np.arange(250, 5251, 500),
)
# ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: '%.0f' % x)))
ax.axvline(
    irt_reserves.index[irt_reserves.index.get_loc(RESERVE_REQ_ABOLISH_DATE)],
    color="k",
    linestyle=":",
    linewidth=1,
)
ax.axvline(
    irt_reserves.index[irt_reserves.index.get_loc(SLR_REINTRODUCTION_DATE)],
    color="k",
    linestyle=":",
    linewidth=1,
)
ax.axvline(
    irt_reserves.index[irt_reserves.index.get_loc(QUANTITATIVE_TIGHTENING_DATE)],
    color="k",
    linestyle=":",
    linewidth=1,
)
x1 = irt_reserves.index[irt_reserves.index.get_loc(RESERVE_REQ_ABOLISH_DATE)]
y1 = irt_reserves.iloc[:, 0].max() * 0.95
x2 = irt_reserves.index[irt_reserves.index.get_loc(RESERVE_REQ_ABOLISH_DATE) - 2]
y2 = y1 + irt_reserves.iloc[:, 0].max() / 15
ax.annotate(
    "Reserve requirements abolished,\nReserve balances excluded from SLR",
    xy=(x1, y1),
    xytext=(x2, y2),
    horizontalalignment="right",
    arrowprops=dict(facecolor="black", shrink=0.05),
)

x1_ = irt_reserves.index[irt_reserves.index.get_loc(SLR_REINTRODUCTION_DATE)]
y1_ = irt_reserves.iloc[:, 0].max() * 1.05
x2_ = irt_reserves.index[irt_reserves.index.get_loc(SLR_REINTRODUCTION_DATE) - 2]
y2_ = y1_ + irt_reserves.iloc[:, 0].max() / 15
ax.annotate(
    "Reserve balances added to SLR",
    xy=(x1_, y1_),
    xytext=(x2_, y2_),
    horizontalalignment="right",
    arrowprops=dict(facecolor="black", shrink=0.05),
)

x1__ = irt_reserves.index[irt_reserves.index.get_loc(QUANTITATIVE_TIGHTENING_DATE)]
y1__ = irt_reserves.iloc[:, 0].max() * 1.12
x2__ = irt_reserves.index[irt_reserves.index.get_loc(QUANTITATIVE_TIGHTENING_DATE) - 2]
y2__ = y1__ + irt_reserves.iloc[:, 0].max() / 15
ax.annotate(
    "Start of quantitative tightening",
    xy=(x1__, y1__),
    xytext=(x2__, y2__),
    horizontalalignment="right",
    arrowprops=dict(facecolor="black", shrink=0.05),
)

_ = ax.legend(loc="upper left")
ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
ax2 = irt_reserves.iloc[:, 2].plot(
    ax=ax2,
    linewidth=2,
    linestyle="-",
    ylabel=RIGHT_Y_AXIS_LABEL,
    xticks=irt_reserves.index[::6],
    color=["#2ca02c", "#d62728"],
)
ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1))
ax2.set_xticklabels(list(map("{:%Y-%m}".format, irt_reserves.index[::6])))
_ = ax2.legend(loc="upper right")


# %%

idxmax_res = irt_reserves.iloc[:, 0].idxmax()
print(
    "Nominal Reserves maximum of  {:>8.2f}bn reached in month {:%Y-%m}".format(
        irt_reserves.loc[idxmax_res].iloc[0], idxmax_res
    )
)
print(
    "Nominal Reserves changed by  {:>+8.2f}bn since (as of month {:%Y-%m})".format(
        irt_reserves.iloc[-1, 0] - irt_reserves.loc[idxmax_res].iloc[0],
        irt_reserves.index[-1],
    )
)
print(
    "Nominal Reserves changed by  {:>+8.2f}bn since {:%Y-%m} to {:.2f}bn".format(
        irt_reserves.iloc[-1, 0] - irt_reserves.iloc[-2, 0],
        irt_reserves.index[-2],
        irt_reserves.iloc[-1, 0],
    )
)
# %%

m2_total = web.get_data_fred("M2NS", start=irt_reserves.index[0]).M2NS

ax = (irt_reserves.iloc[:, 0] / m2_total).plot(
    figsize=(20, 10),
    grid=True,
    title="Reserves Balances/M2",
    xticks=irt_reserves.index[::6],
    xlabel="",
    rot=45,
)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
_ = ax.set_xticklabels(list(map("{:%Y-%m}".format, irt_reserves.index[::6])))
