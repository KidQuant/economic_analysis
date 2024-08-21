# %%
import pandas as pd
import numpy as np
import matplotlib.ticker as mtick
import pandas_datareader.data as web
import datetime as date
from datetime import date
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import MonthBegin

# %%
report_start = date.fromisoformat("1959-01-01")
report_end = date.today()


# %%
cpis = web.get_data_fred(
    [
        "CPIAUCSL",
        "CPILFESL",
        "STICKCPIM158SFRBATL",
        "EXPINF1YR",
        "MICH",
    ],
    start=report_start,
    end=report_end,
)
cpis.iloc[:, 2:] /= 100

# Expected inflation from Reserve Bank of Cleveland needs to be shifted backward by a month givven the way
# the FRED publishes the data
cpis.update(cpis.EXPINF1YR.shift(-1))


cpis.update(cpis.iloc[:, :2].pct_change(12))
cpis.dropna(inplace=True)
# %%

cpis.rename(
    columns={
        "STICKCPIM158SFRBATL": "Sticky CPI (Reservve Bank of Altannta)",
        "EXPINF1YR": "1-Year Expected Inflation (Reserve Bank of Cleveland)",
        "MICH": "1-Year Expected Inflation (University of Michigan)",
    },
    inplace=True,
)

cpis

# %%


def rmse(series_dff):
    return np.sqrt((series_dff**2).mean())


# %%
def construct_rmse_dataframe(date_from=None):
    """
    :param date_from: a datetime.date or pandas.Timestamp object indicating if
                        the calculation of RMSE should be limited to the range of months
                        starting from the given date
    """
    rmse_cpi = []
    rmse_core_cpi = []
    rmse_cpi_exp = []
    rmse_core_cpi_exp = []
    rmse_cpi_mich = []
    rmse_core_cpi_mich = []

    _cpis = cpis if date_from is None else cpis.loc[date_from:]

    idx = pd.Index(
        range(1, 13), name="Sticky CPI/Expected Inflation forward shift in months"
    )
    for i in idx:
        cpis_shifted = pd.concat(
            [_cpis.iloc[:, :2], _cpis.iloc[:, 2:].shift(i)], axis=1
        )
        rmse_cpi.append(rmse(cpis_shifted.iloc[:, 0] - cpis_shifted.iloc[:, 2]))
        rmse_core_cpi.append(rmse(cpis_shifted.iloc[:, 1] - cpis_shifted.iloc[:, 2]))
        rmse_cpi_exp.append(rmse(cpis_shifted.iloc[:, 0] - cpis_shifted.iloc[:, 3]))
        rmse_core_cpi_exp.append(
            rmse(cpis_shifted.iloc[:, 1] - cpis_shifted.iloc[:, 3])
        )
        rmse_cpi_mich.append(rmse(cpis_shifted.iloc[:, 0] - cpis_shifted.iloc[:, 4]))
        rmse_core_cpi_mich.append(
            rmse(cpis_shifted.iloc[:, 1] - cpis_shifted.iloc[:, 4])
        )

    return pd.DataFrame(
        np.array(
            [
                rmse_cpi,
                rmse_core_cpi,
                rmse_cpi_exp,
                rmse_core_cpi_exp,
                rmse_cpi_mich,
                rmse_core_cpi_mich,
            ]
        ).T,
        index=idx,
        columns=[
            "RMSE: CPI and Sticky CPI",
            "RMSE: Core CPI and Sticky CPI",
            "RMSE: CPI and 1y Expected Infl",
            "RMSE: Core CPI and 1y Expected Infl",
            "RMSE: CPI and Mich Infl Exp",
            "RMSE: Core CPI and Mich Infl Exp",
        ],
    )


# %%
df_cpi_predictors = construct_rmse_dataframe()
date_for_last_10y = report_end - relativedelta(years=+10) - MonthBegin()
date_for_last_5y = report_end - relativedelta(years=+5) - MonthBegin()
df_cpi_predictors_last_10y = construct_rmse_dataframe(date_for_last_10y)
df_cpi_predictors_last_5y = construct_rmse_dataframe(date_for_last_5y)

df_cpi_predictors

# %%

_ = df_cpi_predictors.plot(
    figsize=(20, 10),
    grid=True,
    title="Root Mean Square Error (RMSE) between actual CPI and Core CPI predicting metrics (from {:%Y-%m} till {:%Y-%m})".format(
        cpis.index[0].date(), cpis.index[-1].date()
    ),
    xticks=df_cpi_predictors.index,
    style=["", "--"] * 3,
)

# %%
