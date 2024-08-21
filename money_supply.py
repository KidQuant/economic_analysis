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
