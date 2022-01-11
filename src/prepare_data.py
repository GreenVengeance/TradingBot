import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import sys

from config.config import timeframes
import src.T_ as T_


def cleanup_dataframe_for_print(dataframe):
    pd.set_option('expand_frame_repr', False)

    # filter_date = "09/01/22"
    # filter_date = datetime.strptime(filter_date, '%d/%m/%y')
    # dataframe = dataframe[dataframe.date.between(filter_date, (filter_date + timedelta(days=1)))]
    # dataframe = dataframe[dataframe['date'] > filter_date]

    if 'close_time' in dataframe.columns:
        dataframe.pop('close_time')
    if 'trade_number' in dataframe.columns:
        dataframe.pop('trade_number')
    if 'asset_volume' in dataframe.columns:
        dataframe.pop('asset_volume')
    # if '%of_run' in dataframe.columns:
    # dataframe.pop('%of_run')
    if 'esa_C' in dataframe.columns:
        dataframe.pop('esa_C')
    if 'd_C' in dataframe.columns:
        dataframe.pop('d_C')

    return dataframe


def calculate_Heiken_Ashi_columns(df, start_range):
    df['HA_close'] = df.apply(lambda x: (x['open'] + x['high'] + x['low'] + x['close']) / 4, axis=1)

    for i in range(start_range, df.shape[0]):
        if i == 0:
            df.loc[i, 'HA_open'] = (df.loc[i, 'open'] + df.loc[i, 'close']) / 2
        else:
            df.loc[i, 'HA_open'] = (df.loc[i - 1, 'HA_open'] + df.loc[i - 1, 'HA_close']) / 2

    df['HA_high'] = df.apply(lambda x: np.array([x['HA_close'], x['HA_open'], x['high']]).max(0), axis=1)
    df['HA_low'] = df.apply(lambda x: np.array([x['HA_close'], x['HA_open'], x['low']]).min(0), axis=1)

    return df


def calculate_up_down_columns(HA_open, HA_close):
    up_down = ''
    if HA_open < HA_close:
        up_down = '+'
    elif HA_open > HA_close:
        up_down = '-'

    return up_down


def calculate_run_columns(df, i):
    last_symbol = i
    while df.loc[i, 'up(+)_down(-)'] == df.loc[last_symbol, 'up(+)_down(-)']:
        if last_symbol == 0:
            df.loc[i, '%of_run'] = df.loc[i, 'HA_close'] / (df.loc[last_symbol, 'HA_open'] - 1) * 100 - 100
            break
        df.loc[i, '%of_run'] = df.loc[i, 'HA_close'] / (df.loc[last_symbol, 'HA_open'] - 1) * 100 - 100
        last_symbol -= 1

    if i == 0 or i == df.shape[0] - 1 or df.loc[i, 'up(+)_down(-)'] != df.loc[i + 1, 'up(+)_down(-)']:
        df.loc[i, '%_run_total'] = df.loc[i, '%of_run']

    return df


def ema(src, ema_previous_day, length):
    """ Initial EMA --> SMA: SUM(price) / length
    ema_alternative = (1 - alpha) * ema_previous_day + alpha * src"""
    alpha = (2 / (length + 1))
    ema_current = (src - ema_previous_day) * alpha + ema_previous_day

    return ema_current


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


def calculate_indicator_WTwC(df, i):
    """ Indicator: WaveTrend with Crosses [LazyBear]
    n1 and n2 used  as the input lengths for EMAs.
    Making the numbers lower results in more signals, increasing them provides fewer signals"""
    n1 = 10  # Channel Length
    n2 = 21  # Average Length

    if i == (n1 - 1):  # calculate here Initial EMA
        df.loc[i, 'esa_C'] = get_initial_EMA_WT(df, i, -1, n1)
    elif i >= n1:
        ap = (df.loc[i, 'high'] + df.loc[i, 'low'] + df.loc[i, 'close']) / 3
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


def calculate_columns_main(df, start_range):
    df = calculate_Heiken_Ashi_columns(df, start_range)
    df['up(+)_down(-)'] = df.apply(lambda x: calculate_up_down_columns(x['HA_open'], x['HA_close']), axis=1)

    for i in range(start_range, df.shape[0]):
        df = calculate_run_columns(df, i)
        df = calculate_indicator_WTwC(df, i)
    return df


def calculate_HA_open(id, df_copy):
    if id == 0:
        HA_open = (df_copy.loc[id, 'open'] + df_copy.loc[id, 'close']) / 2
    else:
        HA_open = (df_copy.loc[id - 1, 'HA_open'] + df_copy.loc[id - 1, 'HA_close']) / 2
        df_copy.loc[id, 'HA_open'] = HA_open

    return HA_open


def calculate_run_column(id, df_copy):
    last_symbol = id
    while df_copy.loc[id, 'up(+)_down(-)'] == df_copy.loc[last_symbol, 'up(+)_down(-)']:
        if last_symbol == 0:
            df_copy.loc[id, '%of_run'] = df_copy.loc[id, 'HA_close'] / (
                    df_copy.loc[last_symbol, 'HA_open'] - 1) * 100 - 100
            break
        df_copy.loc[id, '%of_run'] = df_copy.loc[id, 'HA_close'] / (df_copy.loc[last_symbol, 'HA_open'] - 1) * 100 - 100
        last_symbol -= 1

    return df_copy.loc[id, '%of_run']


def calculate_run_total(id, df_copy):
    run_total = np.nan
    if id == 0 or id == df_copy.shape[0] - 1 or df_copy.loc[id, 'up(+)_down(-)'] != df_copy.loc[
        id + 1, 'up(+)_down(-)']:
        run_total = df_copy.loc[id, '%of_run']

    return run_total


# TODO:
def update_all_columns(timeframes):
    for i in range(len(timeframes)):
        timeframe = timeframes[i]['file']
        if timeframes[i]['time'] == "1m":
            print("Skip 1m")
            print("\nResults Success updated following: " + timeframe)
        elif timeframes[i]['time'] == "3m":
            print("Skip 3m")
        elif timeframes[i]['time'] == "5m":
            print("Skip 5m")
        elif timeframes[i]['time'] == "15m":
            print("Skip 15m")
        else:
            df = pd.read_feather(timeframe)
            df_copy = pd.read_feather(timeframe)

            # df['HA_close'] = df.apply(lambda x: (x['open'] + x['high'] + x['low'] + x['close']) / 4, axis=1)
            df['HA_open'] = df.apply(lambda x: calculate_HA_open(x['id'], df_copy), axis=1)
            # df['HA_high'] = df.apply(lambda x: np.array([x['HA_close'], x['HA_open'], x['high']]).max(0), axis=1)
            # df['HA_low'] = df.apply(lambda x: np.array([x['HA_close'], x['HA_open'], x['low']]).min(0), axis=1)
            # df['up(+)_down(-)'] = df.apply(lambda x: calculate_up_down_columns(x['HA_open'], x['HA_close']), axis=1)

            # df['%of_run'] = df.apply(lambda x: calculate_run_column(x['id'], df_copy), axis=1)
            # df['%_run_total'] = df.apply(lambda x: calculate_run_total(x['id'], df_copy), axis=1)

            # for i in range(0, df.shape[0]):
            # df = calculate_run_columns(df, i)
            # df = calculate_indicator_WTwC(df, i)

            df.to_feather(timeframe)


def main():
    try:
        # update_all_columns(timeframes)
        # df = pd.read_feather(timeframes[0]['file'])
        print("DF original:")
        # print(cleanup_dataframe_for_print(df))

        # df_test = pd.read_feather(timeframes[0]['file'])
        # df_test = T_.reset_columns(df_test)
        # df_test = calculate_columns_main(df_test, timeframes[0]['file'])
        print("\nDF Test:")
        # print(cleanup_dataframe_for_print(df_test))
        # T_.compare_dataframes(df, df_test)

        for i in range(len(timeframes)):
            df = pd.read_feather(timeframes[i]['file'])
            print("\nResults: " + timeframes[i]['time'])
            df = cleanup_dataframe_for_print(df)
            print(df)



    except Exception as e:
        print(e)
        logging.info(e)


if __name__ == '__main__':
    main()
