from pandas import DataFrame as df
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging
import sys

from config.config import timeframes
import src.prepare_data as func


def filter_date(df, day_start, ONE_DAY):
    filter_date = day_start
    filter_date = datetime.strptime(filter_date, '%Y-%m-%d %H:%M:%S')
    if ONE_DAY:
        df = df[df.date.between(filter_date, (filter_date + timedelta(days=1)))]
    else:
        df = df[df['date'] > filter_date]
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
        if 'id' in dataframe.columns:
            dataframe.pop('id')
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


def get_multilevel_dataframe(timeframes, main_timeframe, day_start, ONE_DAY=True):
    # if ONE_DAY = true: calculate multilevel_dataframe for just given one day
    multilevel_df = {}
    dataframes = {}
    main_timeframe_master_filepath = ""

    for k in range(len(timeframes)):
        current_timeframe = timeframes[k]['time']
        if current_timeframe not in ("1m", "3m", "5m", "3d", "1w", "1M"):

            if current_timeframe == main_timeframe:
                multilevel_df = cleanup_dataframe(timeframes[k], main_timeframe)
                # for now: reset Index
                multilevel_df["id"] = multilevel_df.index
                multilevel_df = filter_date(multilevel_df, day_start, ONE_DAY).reset_index(drop=True)
                main_timeframe_master_filepath = timeframes[k]['master_file']
            else:
                current_df = cleanup_dataframe(timeframes[k], main_timeframe)
                current_df = filter_date(current_df, day_start, ONE_DAY).reset_index(drop=True)
                dataframes[current_timeframe] = current_df

    for j in range(0, multilevel_df.shape[0]):
        for i in range(len(timeframes)):
            current_timeframe = timeframes[i]['time']
            if current_timeframe not in ("1m", "3m", "5m", main_timeframe, "3d", "1w", "1M"):
                current_df = dataframes[current_timeframe]

                if current_timeframe in ("30m", "1h"):
                    if current_timeframe == "30m":
                        matched_date = (multilevel_df.loc[j, "date"]).ceil(freq="30min")
                    else:
                        matched_date = (multilevel_df.loc[j, "date"]).ceil(freq=current_timeframe)

                    WT_EMA_SMA_list = get_WT_EMA_WT_SMA_of_dataframes(matched_date, current_df)
                    multilevel_df.loc[j, current_timeframe + "_WT_EMA"] = WT_EMA_SMA_list[0]
                    multilevel_df.loc[j, current_timeframe + "_WT_SMA"] = WT_EMA_SMA_list[1]

                    # if np.nan in (WT_EMA_SMA_list[1], WT_EMA_SMA_list[0]):
                    # print("-------in j: ", j, "row is missing in timeframe: " + current_timeframe, )

                if current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d"):
                    matched_date = (
                            (multilevel_df.loc[j, "date"] - timedelta(hours=1)).ceil(freq=current_timeframe) + timedelta(hours=1))

                    WT_EMA_SMA_list = get_WT_EMA_WT_SMA_of_dataframes(matched_date, current_df)
                    multilevel_df.loc[j, current_timeframe + "_WT_EMA"] = WT_EMA_SMA_list[0]
                    multilevel_df.loc[j, current_timeframe + "_WT_SMA"] = WT_EMA_SMA_list[1]

    return multilevel_df


def create_masterfile(main_timeframe, day_start):
    # get_multilevel_dataframe(timeframes=timeframes, main_timeframe="15m", day_start=day_start)
    multilevel_df = get_multilevel_dataframe(timeframes=timeframes, main_timeframe="15m", day_start=day_start, ONE_DAY=False)

    print("\n--Success multilevel_dataframe for: " + main_timeframe)
    multilevel_df.to_feather(main_timeframe_master_filepath)


def update_masterfile(main_timeframe):
    for i in range(len(timeframes)):
        current_timeframe = timeframes[i]['time']
        if current_timeframe == main_timeframe:
            old_dataframe = pd.read_feather(timeframes[i]['master_file'])
            last_row = np.nan
            date_of_second_last_row = np.nan

            for j in range(len(old_dataframe) - 1, -1, -1):
                if not np.isnan(old_dataframe.loc[j, "1d_WT_EMA"]):
                    last_row = j
                    date_of_second_last_row = str(old_dataframe.loc[last_row - 1, "date"])
                    break

            old_dataframe = old_dataframe[:last_row]
            new_dataframe = get_multilevel_dataframe(timeframes=timeframes, main_timeframe=main_timeframe,
                                                     day_start=date_of_second_last_row, ONE_DAY=False)

            merged_dataframe = pd.concat([old_dataframe, new_dataframe]).reset_index(drop=True)

            merged_dataframe.to_feather(timeframes[i]['master_file'])
            print("\n--Success multilevel_dataframe for: " + main_timeframe)


def main():
    try:
        pd.set_option('expand_frame_repr', False)
        pd.set_option('display.max_rows', 500)

        # day_start = "01/01/19 00:00"
        day_start = "2020-01-01 00:00:00"
        # create_masterfile("15m", day_start)

        # update_masterfile("15m")

        """
        for i in range(len(timeframes)):
            current_timeframe = timeframes[i]['time']
            if current_timeframe == "15m":
                current_df = pd.read_feather(timeframes[i]['master_file'])
                # current_df = cleanup_dataframe(timeframes[i], "15m")
                # current_df = filter_date(current_df, day_start=day_start,ONE_DAY=False)
                print("\n df: ")
                print(current_df.head(300))
        """



    except Exception as e:
        print(e)
        logging.info(e)


if __name__ == '__main__':
    main()
