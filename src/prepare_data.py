import logging
import sys
from datetime import datetime, timedelta

sys.path.append('/...')
from config.config import timeframes
import src.help_functions as h_
import numpy as np
import pandas as pd


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


def calculate_indicator_WTwC(df, i):
    """ Indicator: WaveTrend with Crosses [LazyBear]
    n1 and n2 used  as the input lengths for EMAs.
    Making the numbers lower results in more signals, increasing them provides fewer signals"""
    n1 = 10  # Channel Length
    n2 = 21  # Average Length

    if i == (n1 - 1):  # calculate here Initial EMA
        df.loc[i, 'esa_C'] = h_.get_initial_EMA_WT(df, i, -1, n1)
    elif i >= n1:
        ap = (df.loc[i, 'high'] + df.loc[i, 'low'] + df.loc[i, 'close']) / 3
        esa = h_.ema(ap, df.loc[i - 1, 'esa_C'], n1)
        df.loc[i, 'esa_C'] = esa

        if i == 18:
            df.loc[i, 'd_C'] = h_.get_initial_EMA_WT(df, i, 8, n1)
        elif i > 18:
            d = h_.ema(abs(ap - esa), df.loc[i - 1, 'd_C'], n1)
            df.loc[i, 'd_C'] = d

    if i == (n2 + 18 - 1):
        tci = h_.get_initial_EMA_WT(df, i, 17, n2)
        df.loc[i, 'WT_EMA'] = tci
    elif i > (n2 + 18 - 1):
        ci = (ap - esa) / (0.015 * d)
        df.loc[i, 'WT_EMA'] = h_.ema(ci, df.loc[i - 1, 'WT_EMA'], n2)
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


def main():
    try:
        pd.set_option('expand_frame_repr', False)
        pd.set_option('display.max_rows', 500)
        # update_all_columns(timeframes)
        # df = pd.read_feather(timeframes[0]['file'])
        # df = calculate_columns_main(df, 0)
        print("DF original:")
        # print(h_.cleanup_dataframe_for_print(df)[9600:].head(100))

        # df_test = pd.read_feather(timeframes[0]['file'])
        # df_test = h_.reset_columns(df_test)
        # df_test = calculate_columns_main(df_test, timeframes[0]['file'])
        print("\nDF Test:")
        # print(h_.cleanup_dataframe_for_print(df_test))
        # h_.compare_dataframes(df, df_test)


    except Exception as e:
        print(e)
        logging.info(e)


if __name__ == '__main__':
    main()
