from pandas import DataFrame as df
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging
import sys

from config.config import timeframes
import src.prepare_data as func


def filter_date_1_day(df, date):
    filter_date = date
    filter_date = datetime.strptime(filter_date, '%d/%m/%y')
    df = df[df.date.between(filter_date, (filter_date + timedelta(days=1)))]
    # df = df[dataframe['date'] > filter_date]
    return df


def cleanup_dataframe(current_timeframe, main_timeframe):
    # dataframe['date'] = pd.to_datetime(dataframe['date']).dt.date
    dataframe = pd.read_feather(current_timeframe['file'])

    if 'open' in dataframe.columns:
        dataframe.pop('open')
    if 'high' in dataframe.columns:
        dataframe.pop('high')
    if 'low' in dataframe.columns:
        dataframe.pop('low')
    if 'volume' in dataframe.columns:
        dataframe.pop('volume')
    if 'close_time' in dataframe.columns:
        dataframe.pop('close_time')
    if 'trade_number' in dataframe.columns:
        dataframe.pop('trade_number')
    if 'asset_volume' in dataframe.columns:
        dataframe.pop('asset_volume')
    if 'HA_open' in dataframe.columns:
        dataframe.pop('HA_open')
    if 'HA_high' in dataframe.columns:
        dataframe.pop('HA_high')
    if 'HA_low' in dataframe.columns:
        dataframe.pop('HA_low')
    if 'esa_C' in dataframe.columns:
        dataframe.pop('esa_C')
    if 'd_C' in dataframe.columns:
        dataframe.pop('d_C')
    if current_timeframe['time'] != main_timeframe:
        if 'close' in dataframe.columns:
            dataframe.pop('close')
        if 'HA_close' in dataframe.columns:
            dataframe.pop('HA_close')
        if 'up(+)_down(-)' in dataframe.columns:
            dataframe.pop('up(+)_down(-)')
        if '%_run_total' in dataframe.columns:
            dataframe.pop('%_run_total')
        if '%of_run' in dataframe.columns:
            dataframe.pop('%of_run')
        if 'id' in dataframe.columns:
            dataframe.pop('id')

    """
    #dataframe['WT_EMA'] = np.nan
    #dataframe['a']['WT_SMA'] = np.nan
    index = pd.MultiIndex.from_product([['30m', '1h'], ['WT_EMA', 'WT_SMA']])
    print(index)
    print(len(dataframe.columns))
    dataframe2 = {}
    dataframe2["15m"] = dataframe.copy().set_index('id')
    dataframe2['30min'] = pd.DataFrame(columns=['id', 'WT_EMA', 'WT_SMA'],
                                             data=(dataframe["id"], dataframe["WT_EMA"], dataframe["WT_SMA"])).set_index('id')
    print(dataframe2)
    """
    return dataframe


def create_multilevel_dataframe():
    day = "08/01/22"
    var = {
        ('30m', 'WT_EMA'): {day: 100},
        ('30m', 'WT_SMA'): {day: 1},
    }
    var2 = {
        ('1h', 'WT_EMA'): {day: 0},
        ('1h', 'WT_SMA'): {day: 0}
    }
    dataframe1 = df(var)
    dataframe2 = df(var2)
    dataframe = pd.concat([dataframe1, dataframe2], axis=1, join='inner')
    # dataframe.loc[0, ["30m"]["WT_SMA"][0]] = np.nan

    # dataframe['30m']['WT_EMA'][0] = 12

    # for i in range(len(timeframes)):
    # current_timeframe = timeframes[i]['time']
    # dataframe = pd.read_feather(timeframes[i]['file'])
    # print(dataframe)

    return dataframe


def get_multilevel_dataframe(timeframes, main_timeframe):
    day = "08/01/22"
    multilevel_dataframe = {}

    for i in range(len(timeframes)):
        current_timeframe = timeframes[i]['time']
        if current_timeframe == main_timeframe:
            multilevel_dataframe = cleanup_dataframe(timeframes[i], main_timeframe)
            multilevel_dataframe = filter_date_1_day(multilevel_dataframe, day)
            multilevel_dataframe["id"] = multilevel_dataframe.copy().reset_index(drop=True).index

    print("--multilevel_dataframe for: " + main_timeframe)
    print(multilevel_dataframe)

    for i in range(len(timeframes)):
        current_timeframe = timeframes[i]['time']
        if current_timeframe in ("1m", "3m", "5m", main_timeframe):
            print("--Skip: " + current_timeframe)
        else:
            multilevel_dataframe[current_timeframe + "_WT_EMA"] = np.nan
            multilevel_dataframe[current_timeframe + "_WT_SMA"] = np.nan

            current_df = cleanup_dataframe(timeframes[i], main_timeframe)
            current_df = filter_date_1_day(current_df, day)
            # TODO:

            print("\nResults: " + current_timeframe)
            print(current_df)

    print("\n--multilevel_dataframe for: " + main_timeframe)
    print(multilevel_dataframe)

    return multilevel_dataframe


def main():
    try:
        pd.set_option('expand_frame_repr', False)
        df = get_multilevel_dataframe(timeframes, main_timeframe="15m")

        """
        if current_timeframe == "4h":
            print("\n --------------- Type:")
            for j in range(0, df.shape[0]):
                print(df.loc[df.index[j], 'date'])

            break

        df['date'] = pd.to_datetime(df['date']).dt.date
        for i in range(df.index[0], df.shape[0] + df.index[0]):
            date = df.loc[i, 'date']
            print(date)
        """

    except Exception as e:
        print(e)
        logging.info(e)


if __name__ == '__main__':
    main()
