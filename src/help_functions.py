# import logging
# import sys
# from datetime import datetime, timedelta

import numpy as np
# import pandas as pd
from pandas import DataFrame as df

sys.path.append('/Users/AhmedMajid/PycharmProjects/TradingBot')
# from config.config import timeframes, KPIS_path, ema_means_path, ema_medians_path
import src.prepare_data as func


# ---------------------------------------------------- for prepare_data_py
def cleanup_dataframe_for_print(dataframe):
    pd.set_option('expand_frame_repr', False)

    if 'close_time' in dataframe.columns:
        dataframe.pop('close_time')
    if 'trade_number' in dataframe.columns:
        dataframe.pop('trade_number')
    if 'asset_volume' in dataframe.columns:
        dataframe.pop('asset_volume')
    if 'esa_C' in dataframe.columns:
        dataframe.pop('esa_C')
    if 'd_C' in dataframe.columns:
        dataframe.pop('d_C')

    return dataframe


def get_initial_EMA_WT(df, i, stop, n):
    initial = []
    if i == 9:
        while i != stop:
            ap = (df.loc[i, 'high'] + df.loc[i, 'low'] + df.loc[i, 'close']) / 3
            initial.append(ap)
            i -= 1

    elif i == 18:
        while i != stop:
            ap = (df.loc[i, 'high'] + df.loc[i, 'low'] + df.loc[i, 'close']) / 3
            esa = df.loc[i, 'esa_C']
            initial.append(abs(ap - esa))
            i -= 1

    elif i == 38:
        while i != stop:
            ap = (df.loc[i, 'high'] + df.loc[i, 'low'] + df.loc[i, 'close']) / 3
            esa = df.loc[i, 'esa_C']
            d = df.loc[i, 'd_C']
            ci = (ap - esa) / (0.015 * d)
            initial.append(ci)
            i -= 1

    if len(initial) == n:
        initial = np.mean(initial)

    # print("___________Success")
    return initial


def ema(src, ema_previous_day, length):
    """ Initial EMA --> SMA: SUM(price) / length
    ema_alternative = (1 - alpha) * ema_previous_day + alpha * src"""
    alpha = (2 / (length + 1))
    ema_current = (src - ema_previous_day) * alpha + ema_previous_day

    return ema_current


# ----------- for testing dfs
def reset_columns(df):
    df['HA_open'] = np.nan
    df['HA_high'] = np.nan
    df['HA_low'] = np.nan
    df['HA_close'] = np.nan
    df['up(+)_down(-)'] = np.nan
    df['%of_run'] = np.nan
    df['%_run_total'] = np.nan
    # df['WT_EMA'] = np.nan
    # df['WT_SMA'] = np.nan

    return df


def compare_dataframes(df1, df2):
    for i in range(0, df1.shape[0]):
        if df1.loc[i, 'HA_open'] != df2.loc[i, 'HA_open']:
            print("OPEN False df1: ", df1.loc[i, 'HA_open'], " df2: ", df2.loc[i, 'HA_open'])

        if df1.loc[i, 'HA_high'] != df2.loc[i, 'HA_high']:
            print("HIGH False df1: ", df1.loc[i, 'HA_high'], " df2: ", df2.loc[i, 'HA_high'])

        if df1.loc[i, 'HA_low'] != df2.loc[i, 'HA_low']:
            print("LOW False df1: ", df1.loc[i, 'HA_low'], " df2: ", df2.loc[i, 'HA_low'])

        if df1.loc[i, 'HA_close'] != df2.loc[i, 'HA_close']:
            print("CLOSE False df1: ", df1.loc[i, 'HA_close'], " df2: ", df2.loc[i, 'HA_close'])

        if df1.loc[i, 'up(+)_down(-)'] != df2.loc[i, 'up(+)_down(-)']:
            print("up(+)_down(-) False df1: ", df1.loc[i, 'up(+)_down(-)'], " df2: ", df2.loc[i, 'up(+)_down(-)'])
    print('\nSuccess --T_compare_dataframes --if no False all rows are the same')


def compare_dataframes2(df1, df2):
    df = pd.DataFrame(columns=['WT_EMA',
                               'WT_EMA_HA',
                               'WT_SMA',
                               'WT_SMA_HA',
                               'WT_Compare',
                               'WT_Compare_HA',
                               'C_EMA', 'C_SMA'])

    for i in range(0, df1.shape[0]):
        df.loc[i, 'WT_Compare'] = df1.loc[i, 'WT_Compare'] = abs(df1.loc[i, 'WT_SMA'] - df1.loc[i, 'WT_EMA'])
        df.loc[i, 'WT_Compare_HA'] = df2.loc[i, 'WT_Compare'] = abs(df2.loc[i, 'WT_SMA'] - df2.loc[i, 'WT_EMA'])
        df.loc[i, 'WT_EMA'] = df1.loc[i, 'WT_SMA']
        df.loc[i, 'WT_SMA'] = df1.loc[i, 'WT_EMA']
        df.loc[i, 'WT_EMA_HA'] = df2.loc[i, 'WT_SMA']
        df.loc[i, 'WT_SMA_HA'] = df2.loc[i, 'WT_EMA']
        df.loc[i, 'C_EMA'] = df.loc[i, 'WT_EMA'] - df.loc[i, 'WT_EMA_HA']
        df.loc[i, 'C_SMA'] = df.loc[i, 'WT_SMA'] - df.loc[i, 'WT_SMA_HA']

    print(df.tail(60))


def EMA():
    DATA = [22.27, 22.19, 22.08, 22.17, 22.18, 22.13, 22.23, 22.43, 22.24, 22.29, 22.15, 22.39, 22.38, 22.61, 23.36,
            24.05, 23.75, 23.83, 23.95, 23.63, 23.82, 23.87, 23.65, 23.19, 23.10, 23.33, 22.68, 23.10, 22.40, 22.17,
            24.05, 23.75, 23.83, 23.95, 23.63, 23.82, 23.87, 23.65, 23.19, 23.10, 23.33, 22.68, 23.10, 22.40, 22.17]

    df = pd.DataFrame(DATA, columns=['price'])
    df['ema'] = np.nan
    df['esa_C'] = np.nan
    df['d_C'] = np.nan
    df['WT_EMA'] = np.nan
    df['WT_SMA'] = np.nan

    return df


def get_initial_EMA_WT_HA(df, i, stop, n):
    initial = []
    if i == 9:
        while i != stop:
            ap = (df.loc[i, 'HA_high'] + df.loc[i, 'HA_low'] + df.loc[i, 'HA_close']) / 3
            initial.append(ap)
            i -= 1

    elif i == 18:
        while i != stop:
            ap = (df.loc[i, 'HA_high'] + df.loc[i, 'HA_low'] + df.loc[i, 'HA_close']) / 3
            esa = df.loc[i, 'esa_C']
            initial.append(abs(ap - esa))
            i -= 1

    elif i == 38:
        while i != stop:
            ap = (df.loc[i, 'HA_high'] + df.loc[i, 'HA_low'] + df.loc[i, 'HA_close']) / 3
            esa = df.loc[i, 'esa_C']
            d = df.loc[i, 'd_C']
            ci = (ap - esa) / (0.015 * d)
            initial.append(ci)
            i -= 1

    if len(initial) == n:
        initial = np.mean(initial)

    # print("___________Success")
    return initial


def calculate_indicator_WTwC_HA(df, i):
    """ Indicator: WaveTrend with Crosses [LazyBear]
    n1 and n2 used  as the input lengths for EMAs.
    Making the numbers lower results in more signals, increasing them provides fewer signals"""
    n1 = 10  # Channel Length
    n2 = 21  # Average Length

    if i == (n1 - 1):  # calculate here Initial EMA
        df.loc[i, 'esa_C'] = get_initial_EMA_WT(df, i, -1, n1)
    elif i >= n1:
        ap = (df.loc[i, 'HA_high'] + df.loc[i, 'HA_low'] + df.loc[i, 'HA_close']) / 3
        esa = ema(ap, df.loc[i - 1, 'esa_C'], n1)
        df.loc[i, 'esa_C'] = esa

        if i == 18:
            df.loc[i, 'd_C'] = get_initial_EMA_WT(df, i, 8, n1)
        elif i > 18:
            d = ema(abs(ap - esa), df.loc[i - 1, 'd_C'], n1)
            df.loc[i, 'd_C'] = d

    if i == (n2 + 18 - 1):
        tci = get_initial_EMA_WT(df, i, 17, n2)
        df.loc[i, 'WT_EMA'] = tci
    elif i > (n2 + 18 - 1):
        ci = (ap - esa) / (0.015 * d)
        df.loc[i, 'WT_EMA'] = ema(ci, df.loc[i - 1, 'WT_EMA'], n2)
    if i >= 41:
        sma = np.mean([df.loc[i, 'WT_EMA'], df.loc[i - 1, 'WT_EMA'], df.loc[i - 2, 'WT_EMA'], df.loc[i - 3, 'WT_EMA']])
        df.loc[i, 'WT_SMA'] = sma

    return df


# ---------------------------------------------------- for analyse.py
def get_WT_EMA_WT_SMA_of_dataframes(matched_date, current_df):
    list = [np.nan, np.nan]

    if matched_date <= current_df.iloc[-1]["date"]:
        current_row_of_matched_df = current_df.loc[current_df["date"] == matched_date].reset_index(drop=True)
        if not current_row_of_matched_df.empty:
            WT_EMA = current_row_of_matched_df.loc[0, "WT_EMA"]
            WT_SMA = current_row_of_matched_df.loc[0, "WT_SMA"]
            list[0] = WT_EMA
            list[1] = WT_SMA

    """# to check if current df is alright
    if np.nan in (list[1], list[0]):
        print("\n---------------------------matched_date: ", matched_date)
        print(current_df)
    """
    return list
