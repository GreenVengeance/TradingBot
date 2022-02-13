import logging
import sys
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pandas import DataFrame as df

sys.path.append('/...')
from config.keys import client
from config.config import coin, timeframes
import src.prepare_data as func
import src.help_functions as h_


def get_current_BTC():
    prices = client.get_symbol_ticker(symbol=coin)
    dataframe = pd.DataFrame(prices, index=[0])
    BTC_price = float(dataframe.loc[0, 'price'])

    return BTC_price


def create_dataFrame(coin, timeframe, start_date, end_date):
    candles = client.get_historical_klines(symbol=coin, interval=timeframe, start_str=start_date, end_str=end_date)
    dataframe = df(candles,
                   columns=['date', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'asset_volume',
                            'trade_number', 'taker_buy_base', 'taker_buy_quote', 'can_be_ignored'])
    # cleanup dataframe:
    dataframe.pop('taker_buy_base')
    dataframe.pop('taker_buy_quote')
    dataframe.pop('can_be_ignored')

    # reformat columns
    for i in range(dataframe.shape[0]):
        dataframe.loc[i, 'date'] = datetime.fromtimestamp(int(dataframe.loc[i, 'date'] / 1000))
        dataframe.loc[i, 'close_time'] = datetime.fromtimestamp(int(dataframe.loc[i, 'close_time'] / 1000))
        dataframe.loc[i, 'open'] = float(dataframe.loc[i, 'open'])
        dataframe.loc[i, 'high'] = float(dataframe.loc[i, 'high'])
        dataframe.loc[i, 'low'] = float(dataframe.loc[i, 'low'])
        dataframe.loc[i, 'close'] = float(dataframe.loc[i, 'close'])
        # dataframe.loc[i, 'asset_volume'] = float(dataframe.loc[i, 'asset_volume'])
        dataframe.loc[i, 'trade_number'] = int(dataframe.loc[i, 'trade_number'])

    # create new columns:
    dataframe['HA_open'] = np.nan
    dataframe['HA_high'] = np.nan
    dataframe['HA_low'] = np.nan
    dataframe['HA_close'] = np.nan
    dataframe['up(+)_down(-)'] = np.nan
    dataframe['%of_run'] = np.nan
    dataframe['%_run_total'] = np.nan
    dataframe['esa_C'] = np.nan  # C stands for Cache or Calculation Value
    dataframe['d_C'] = np.nan
    dataframe['WT_EMA'] = np.nan
    dataframe['WT_SMA'] = np.nan

    return dataframe


def format_datetime(date):
    time = int(datetime.timestamp(date)) * 1000
    return time


def download_ALL_historical_data():
    start_date = '31 Dec, 2018'
    end_date = format_datetime(datetime.now())

    for i in range(len(timeframes)):
        dataframe = create_dataFrame(coin, timeframes[i]['time'], start_date, end_date)
        dataframe.to_feather(timeframes[i]['file'])
        print('Success downloaded ALL_historical_data: ' + timeframes[i]['time'])


def update_historical_data():
    second_last_row = -2
    for i in range(len(timeframes)):
        timeframe = timeframes[i]['time']
        old_dataframe = pd.read_feather(timeframes[i]['file'])
        if old_dataframe.loc[old_dataframe.shape[0] - 1, "id"] == 0:
            old_dataframe = old_dataframe[:-1]

        time_of_second_last_row = format_datetime(old_dataframe['date'].iloc[second_last_row])

        old_dataframe = old_dataframe[:second_last_row]
        new_dataframe = create_dataFrame(coin, timeframe, time_of_second_last_row, format_datetime(datetime.now()))
        merged_dataframe = pd.concat([old_dataframe, new_dataframe]).reset_index(drop=True)

        if timeframe != "1m":
            merged_dataframe = func.calculate_columns_main(merged_dataframe, old_dataframe.shape[0])
        merged_dataframe["id"] = merged_dataframe.index
        merged_dataframe.to_feather(timeframes[i]['file'])
        print('--Success update_historical_data for: ' + timeframe)


def forecast_timeframes():
    for i in range(len(timeframes)):
        current_timeframe = timeframes[i]['time']
        if current_timeframe == "15m":
            fifteen_min_df = pd.read_feather(timeframes[i]['file'])
            last_row_fifteen_min = fifteen_min_df[fifteen_min_df.shape[0] - 1:].reset_index(drop=True)
            last_row_fifteen_min.loc[0, "id"] = 0

        if current_timeframe not in ("1m", "3m", "5m", "15m"):
            current_df = pd.read_feather(timeframes[i]['file'])
            if current_df.loc[current_df.shape[0] - 1, "id"] == 0:
                current_df = current_df[:-1]
            date = h_.get_matched_date(current_timeframe, last_row_fifteen_min.loc[0, "date"])
            last_row = current_df.shape[0] - 1
            if date != current_df.loc[last_row, "date"]:
                current_df = pd.concat([current_df, last_row_fifteen_min]).reset_index(drop=True)
                last_row = current_df.shape[0] - 1
                if current_timeframe == "3d":
                    current_df.loc[last_row, "date"] = current_df.loc[last_row - 1, "date"] + timedelta(days=3)
                elif current_timeframe == "1w":
                    current_df.loc[last_row, "date"] = current_df.loc[last_row - 1, "date"] + timedelta(weeks=1)
                elif current_timeframe == "1M":
                    current_df.loc[last_row, "date"] = current_df.loc[last_row - 1, "date"] + timedelta(days=31)
                else:
                    current_df.loc[last_row, "date"] = date

            current_df = func.calculate_columns_main(current_df, last_row - 1)
            current_df.to_feather(timeframes[i]['file'])
            print("\n--Success forecasted last row for :" + current_timeframe)
            # print(h_.cleanup_dataframe_for_print(current_df).tail(5))


def update_historical_data_reverse(day):
    for i in range(len(timeframes)):
        # if timeframes[i]['time'] != "1m":
        # start_date = format_datetime(pd.read_feather(timeframes[0]['file'])['date'].iloc[0])
        old_dataframe = pd.read_feather(timeframes[i]['file'])
        start_date = format_datetime((old_dataframe['date'].iloc[0] - timedelta(days=day)))
        end_date = format_datetime(old_dataframe['date'].iloc[0])

        old_dataframe = old_dataframe.iloc[1:, :]
        new_dataframe = create_dataFrame(coin, timeframes[i]['time'], start_date, end_date)

        merged_dataframe = pd.concat([new_dataframe, old_dataframe]).reset_index(drop=True)
        merged_dataframe["id"] = merged_dataframe.index
        # merged_dataframe = func.calculate_columns_main(merged_dataframe, old_dataframe.shape[0])

        merged_dataframe.to_feather(timeframes[i]['file'])
        print('--Success update_hist_data_reverse for: ' + timeframes[i]['time'] + " first Date:",
              merged_dataframe['date'].iloc[0])


def reformate_date_column():
    for i in range(len(timeframes)):
        current_timeframe = timeframes[i]['time']
        if current_timeframe == "1d" or current_timeframe == "12h" or current_timeframe == "8h" \
                or current_timeframe == "6h" or current_timeframe == "4h" or current_timeframe == "2h":
            current_df = pd.read_feather(timeframes[i]['file'])

            for j in range(0, current_df.shape[0]):
                list = str(current_df.loc[j, "date"]).split()
                if current_timeframe == "1d" and list[1] == '02:00:00':
                    current_df.loc[j, "date"] -= timedelta(hours=1)

                if current_timeframe == "12h" and (list[1] == '02:00:00' or list[1] == '14:00:00'):
                    current_df.loc[j, "date"] -= timedelta(hours=1)

                if current_timeframe == "8h" and (
                        list[1] == '02:00:00' or list[1] == '10:00:00' or list[1] == '18:00:00'):
                    current_df.loc[j, "date"] -= timedelta(hours=1)

                if current_timeframe == "6h" and (
                        list[1] == '02:00:00' or list[1] == '08:00:00' or
                        list[1] == '14:00:00' or list[1] == '20:00:00'):
                    current_df.loc[j, "date"] -= timedelta(hours=1)

                if current_timeframe == "4h" and (
                        list[1] == '02:00:00' or list[1] == '06:00:00' or list[1] == '10:00:00' or
                        list[1] == '14:00:00' or list[1] == '18:00:00' or list[1] == '22:00:00'):
                    current_df.loc[j, "date"] -= timedelta(hours=1)

                if current_timeframe == "2h" and (
                        list[1] == '02:00:00' or list[1] == '04:00:00' or list[1] == '06:00:00' or
                        list[1] == '08:00:00' or list[1] == '10:00:00' or list[1] == '12:00:00' or
                        list[1] == '14:00:00' or list[1] == '16:00:00' or list[1] == '18:00:00' or
                        list[1] == '20:00:00' or list[1] == '22:00:00' or list[1] == '00:00:00'):
                    current_df.loc[j, "date"] -= timedelta(hours=1)

            current_df.to_feather(timeframes[i]['file'])
            print('--Success reformate_date_column for: ' + current_timeframe)


def main():
    try:
        pd.set_option('expand_frame_repr', False)
        pd.set_option('display.max_rows', 100)
        # download_ALL_historical_data()
        # reformate_date_column()
        # update_historical_data()

        for i in range(len(timeframes)):
            if timeframes[i]['time'] in ('2h',):
                current_df = pd.read_feather(timeframes[i]['file'])
                print("\nResults: " + timeframes[i]['time'])
                print(h_.cleanup_dataframe_for_print(current_df))
                print("\nResults2: " + timeframes[i]['time'])
                print(current_df.loc[current_df.shape[0] - 1, "id"])
                print(current_df.loc[-1, "id"])

    except Exception as e:
        print(e)
        logging.info(e)


if __name__ == '__main__':
    main()
