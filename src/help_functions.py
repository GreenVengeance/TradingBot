# import sys
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go
from dash import dash_table
# from config.config import timeframes, KPIS_path, ema_means_path, ema_medians_path
import src.prepare_data as func
import pandas as pd
from pandas import DataFrame as df


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
    list = [np.nan, np.nan, np.nan]

    if matched_date <= current_df.iloc[-1]["date"]:
        current_row_of_matched_df = current_df.loc[current_df["date"] == matched_date].reset_index(drop=True)
        if not current_row_of_matched_df.empty:
            WT_EMA = current_row_of_matched_df.loc[0, "WT_EMA"]
            WT_SMA = current_row_of_matched_df.loc[0, "WT_SMA"]
            id = current_row_of_matched_df.loc[0, "id"]
            list = [WT_EMA, WT_SMA, id]

    """# to check if current df is alright
    if np.nan in (list[1], list[0]):
        print("\n---------------------------matched_date: ", matched_date)
        print(current_df)
    """
    return list


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
        # if 'id' in dataframe.columns:
        # dataframe.pop('id')
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


def filter_date(df, day_start, ONE_DAY=False):
    filter_date = day_start
    filter_date = datetime.strptime(filter_date, '%Y-%m-%d %H:%M:%S')
    if ONE_DAY:
        df = df[df.date.between(filter_date, (filter_date + timedelta(days=1)))]
    else:
        df = df[df['date'] > filter_date]
    return df


def get_fig(timframe, Long_Short, first_last=""):
    if Long_Short == "long":
        color = "green"
    elif Long_Short == "short":
        color = "red"
    else:
        color = "black"

    if timframe == "15m":
        x = 15
    elif timframe == "30m":
        x = 30
    elif timframe == "1h":
        x = 60
    elif timframe == "2h":
        x = 120
    elif timframe == "4h":
        x = 240
    elif timframe == "6h":
        x = 360
    elif timframe == "8h":
        x = 480
    elif timframe == "12h":
        x = 720
    elif timframe == "1d":
        x = 1440
    elif timframe == "3d":
        x = 4320

    if first_last == "first":
        x = 60
    elif first_last == "last":
        x -= 60

    return go.Bar(
        x=[x, 0, 0], y=[timframe],
        name=Long_Short,
        orientation='h',
        marker=dict(
            color=color,
            line=dict(color='black', width=3)
        )
    )


def get_matched_date(current_timeframe, date):
    matched_date = date
    if current_timeframe == "30m":
        matched_date = date.ceil(freq="30min")
    elif current_timeframe == "1h":
        matched_date = date.ceil(freq=current_timeframe)
    elif current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d"):
        matched_date = ((date - timedelta(hours=1)).ceil(freq=current_timeframe) + timedelta(hours=1))

    return matched_date


# ---------------------------------------------------- for python_app.py
def get_options(timeframes):
    dict_list = []
    for i in timeframes:
        dict_list.append({'label': i, 'value': i})
        # dict_list.append({'label': i, 'value': dataframes_ups[i]})

    return dict_list


def get_dash_table(df, string):
    return dash_table.DataTable(
        id='datatable_' + string,
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
            if i == "id"
            else {"name": i, "id": i, "deletable": True, "selectable": True}
            for i in df.columns
        ],
        data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="multi",
        row_selectable="multi",
        row_deletable=True,
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell={'minWidth': '130px', 'maxWidth': '140px', 'width': '140px', 'color': 'black'},
        style_header={'backgroundColor': 'lightgrey'},
        style_cell_conditional=[{
            'if': {'column_id': c},
            'textAlign': 'left', 'minWidth': '160px'
        } for c in ['date']],
        style_data={'whiteSpace': 'normal', 'height': 'auto'},
        fill_width=False
    )


def get_kpi_table(df):
    return dash_table.DataTable(
        id='datatable_kpis',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
            if i == "id"
            else {"name": i, "id": i, "deletable": True, "selectable": True}
            for i in df.columns
        ],
        data=df.to_dict('records'),
        column_selectable="multi",
        row_selectable="multi",
        page_action="native",
        style_cell={'minWidth': '75px', 'maxWidth': '140px', 'width': '140px', 'color': 'black'},
        style_header={'backgroundColor': 'lightgrey'},
        style_cell_conditional=[{
            'if': {'column_id': c},
            'textAlign': 'left',
            'minWidth': '70px'
        } for c in ["stage", "kind"]],
        style_data={'whiteSpace': 'normal', 'height': 'auto'},
        style_data_conditional=[
            {'if': {'row_index': 3},
             'backgroundColor': '#3D9970', 'color': 'white'},
            {'if': {'row_index': 4},
             'backgroundColor': '#3D9970', 'color': 'white'},
            {'if': {'row_index': 5},
             'backgroundColor': '#3D9970', 'color': 'white'},
            {'if': {'filter_query': '{kind} = "%"', 'column_id': 'kind'},
             'backgroundColor': '#FF4136', 'color': 'white'}]
    )


# ---------------------------------------------------- for one_percent.py
# delete later
def forecast_masterfile_15m():
    # print(timeframes[6]['time'])
    master_df = pd.read_feather(timeframes[3]['master_file'])
    fifteen_min_df = pd.read_feather(timeframes[3]['file'])
    two_hours_df = pd.read_feather(timeframes[6]['file'])

    last_row_fifteen_min = fifteen_min_df[fifteen_min_df.shape[0] - 1:].reset_index(drop=True)
    last_row_fifteen_min.loc[0, "id"] = "x"
    for i in range(len(timeframes)):
        current_timeframe = timeframes[i]['time']
        if current_timeframe not in ("1m", "3m", "5m", "15m"):
            current_df = pd.read_feather(timeframes[i]['file'])
            date = h_.get_matched_date(current_timeframe, last_row_fifteen_min.loc[0, "date"])
            if date != current_df.loc[current_df.shape[0] - 1, "date"]:
                current_df = pd.concat([current_df, last_row_fifteen_min]).reset_index(drop=True)

                if current_timeframe == "3d":
                    current_df.loc[current_df.shape[0] - 1, "date"] = current_df.loc[
                                                                          current_df.shape[0] - 2, "date"] + timedelta(
                        days=3)
                elif current_timeframe == "1w":
                    current_df.loc[current_df.shape[0] - 1, "date"] = current_df.loc[
                                                                          current_df.shape[0] - 2, "date"] + timedelta(
                        weeks=1)
                elif current_timeframe == "1M":
                    current_df.loc[current_df.shape[0] - 1, "date"] = current_df.loc[
                                                                          current_df.shape[0] - 2, "date"] + timedelta(
                        days=31)
                else:
                    current_df.loc[current_df.shape[0] - 1, "date"] = date
            print("\ndf for :" + current_timeframe)
            print(h_.cleanup_dataframe_for_print(current_df.tail(5)))

    print("\nMaster:")
    # print(master_df.tail(40))

    # two_hours_df = add_new_row_to_df(two_hours_df, current_row_fifteen_min)
    print("\n2h NEW:")
    # print(h_.cleanup_dataframe_for_print(two_hours_df.tail(7)))


# delete later
def add_new_row_to_df(current_df, current_rows):
    for j in range(len(current_df) - 1, -1, -1):
        if current_df.loc[j, "date"] < current_rows.loc[0, "date"]:
            current_df = current_df[:j + 1]
            break

    merged_df = current_df.copy()
    merged_df_two = current_df.copy()
    for i in range(current_rows.shape[0]):
        current_row = current_rows[:i + 1][i:]
        if i == (current_rows.shape[0] - 1) \
                or current_row.loc[i, "date"] == merged_df.loc[merged_df.shape[0] - 1, "date"] + timedelta(hours=2):
            merged_df = pd.concat([merged_df, current_row]).reset_index(drop=True)

    merged_df = func.calculate_columns_main(merged_df, current_df.shape[0] - 1)

    print("\n2h NEW:")
    print(h_.cleanup_dataframe_for_print(merged_df).tail(7))

    high = 0
    low = 0
    for i in range(current_rows.shape[0]):
        current_row = current_rows[:i + 1][i:]

        if high < current_row.loc[i, "high"]:
            high = current_row.loc[i, "high"]
        if low > current_row.loc[i, "low"] or low == 0:
            low = current_row.loc[i, "low"]

        if i == (current_rows.shape[0] - 1) or current_row.loc[i, "date"] == merged_df_two.loc[
            merged_df_two.shape[0] - 1, "date"] + timedelta(hours=2):
            current_row.loc[i, "high"] = high
            current_row.loc[i, "low"] = low
            merged_df_two = pd.concat([merged_df_two, current_row]).reset_index(drop=True)
            high = 0
            low = 0
    merged_df_two = func.calculate_columns_main(merged_df_two, current_df.shape[0] - 1)

    print("\n2h NEW_2:")
    print(h_.cleanup_dataframe_for_print(merged_df_two).tail(7))

    return merged_df
