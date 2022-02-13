import sys
import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

sys.path.append('/...')
from config.config import timeframes, KPIS_path
import src.prepare_data as func
import src.analyse as analyse
import src.help_functions as h_


def get_df(timeframe_label, cols, date_filter=False, date=""):
    current_df = pd.read_feather(timeframe_label)
    if date_filter:
        current_df = h_.filter_date(current_df, date)
    current_df['index'] = current_df.reset_index(drop=True).index
    current_df.set_index('index', inplace=True, drop=False)
    current_df[cols] = current_df[cols].round(2)

    return current_df


day_start = "2021-01-01 00:00:00"
dataframes = {}
timeframe_list = []  # ['1m', ..., '1d']
for i in range(len(timeframes)):
    current_timeframe = timeframes[i]['time']
    timeframe_list.append(current_timeframe)
    cols_1 = ["open", "high", "low", "close", "volume", "%of_run", "%_run_total",
              "HA_open", "HA_high", "HA_low", "HA_close", "WT_EMA", "WT_SMA"]
    current_df = get_df(timeframes[i]['file'], cols_1, date_filter=True, date=day_start)
    if 'id' in current_df.columns:
        current_df.pop('id')
    dataframes[current_timeframe] = h_.cleanup_dataframe_for_print(current_df)

dataframes_ups = {}
timeframe_list_ups = []  # ['15m','30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d']
for i in range(len(timeframes)):
    current_timeframe = timeframes[i]['time']
    if current_timeframe == "15m":
        timeframe_list_ups.append(current_timeframe)
        cols_2 = ["close", "HA_close", "%of_run", "%_run_total", "WT_EMA", "WT_SMA", "30m_WT_EMA", "30m_WT_SMA",
                  "1h_WT_EMA", "2h_WT_EMA", "4h_WT_EMA", "6h_WT_EMA", "8h_WT_EMA", "12h_WT_EMA", "1d_WT_EMA",
                  "1h_WT_SMA", "2h_WT_SMA", "4h_WT_SMA", "6h_WT_SMA", "8h_WT_SMA", "12h_WT_SMA", "1d_WT_SMA"]
        master_ups_df = get_df(timeframes[3]['master_file_ups'], cols_2)

        dataframes_ups[current_timeframe] = master_ups_df

    elif current_timeframe not in ("1m", "3m", "5m", "15m", "3d", "1w", "1M"):
        timeframe_list_ups.append(current_timeframe)
        cols = ["close", "HA_close", "%of_run", "%_run_total", "WT_EMA", "WT_SMA"]
        current_df = get_df(timeframes[i]['ups'], cols)

        dataframes_ups[current_timeframe] = current_df


def create_left_children_list():
    children = [html.H2('BTC - Timeframes'), html.P('''Select a default timeframes:'''),
                html.Div(children=[dcc.Input(id="input", type="text", placeholder="", debounce=True, value=day_start)]),
                html.Div(className='div-for-dropdown',
                         children=[dcc.Dropdown(id='timeframeselector_input',
                                                options=h_.get_options(timeframe_list),
                                                multi=True, value=[],
                                                style={'backgroundColor': '#1E1E1E'},
                                                className='timeframeselector_input')],
                         style={'color': '#1E1E1E'}),
                html.P('''Select timeframes for df_Ups(+):'''),
                html.Div(className='div-for-dropdown',
                         children=[dcc.Dropdown(id='timeframeselector_ups_input',
                                                options=h_.get_options(timeframe_list_ups),
                                                multi=True, value=[],
                                                style={'backgroundColor': '#1E1E1E'},
                                                className='timeframeselector_ups_input')],
                         style={'color': '#1E1E1E'})]

    return children


def create_right_children_list():
    children = [html.H1(
        children='The One percent -- Dashboard',
        style={'textAlign': 'center'}),
        html.H3('--Current KPIs'), h_.get_kpi_table(analyse.merge_KPIsDF_mean_median()),
        html.H3('--Latest two runs of: 15m_master'),
        h_.get_dash_table(analyse.get_last_row_runs_of_master("15m"), "15m_master"),
        html.Div(dcc.Graph(id="g1", figure=analyse.create_nested_bar_chart())),
        html.Div(id='timeseries_output', children=[]), html.Br(),
        html.Div(id='timeseries_ups_output', children=[]), html.Br(),
        # html.Div(id='#1-container'), html.Div(id='#2-container')
    ]

    return children


# -------------------------------------------------------------------------------------
app = dash.Dash(__name__, prevent_initial_callbacks=True)

# See --> (https://dash.plotly.com/datatable/filtering)
app.layout = html.Div(children=[html.Div(className='row', children=[
    html.Div(className='two columns div-user-controls', children=create_left_children_list()),
    html.Div(className='ten columns div-for-charts bg-grey', children=create_right_children_list())
])
                                ])


@app.callback(Output('timeseries_output', 'children'),
              Input("input", "value"),
              [Input('timeframeselector_input', 'value')])
def update_timeseries(input, selected_dropdown_value):
    timeseries_list = []

    for timeframe in selected_dropdown_value:
        timeseries_list.append(html.H3('--Dataframe for: ' + timeframe))
        if input != day_start:
            i = next((index for (index, d) in enumerate(timeframes) if d["time"] == timeframe), None)
            current_df = get_df(timeframes[i]['file'], cols_1, date_filter=True, date=input)
            if 'id' in current_df.columns:
                current_df.pop('id')
            if 'close_time' in current_df.columns:
                current_df.pop('close_time')
            if 'trade_number' in current_df.columns:
                current_df.pop('trade_number')
            if 'asset_volume' in current_df.columns:
                current_df.pop('asset_volume')
            if 'esa_C' in current_df.columns:
                current_df.pop('esa_C')
            if 'd_C' in current_df.columns:
                current_df.pop('d_C')
            timeseries_list.append(h_.get_dash_table(current_df, timeframe))
        else:
            current_df = dataframes[timeframe]
            timeseries_list.append(h_.get_dash_table(current_df, timeframe))

    return timeseries_list


@app.callback(Output('timeseries_ups_output', 'children'),
              [Input('timeframeselector_ups_input', 'value')])
def update_timeseries_ups(selected_dropdown_value):
    timeseries_list = []
    for timeframe in selected_dropdown_value:
        timeseries_list.append(html.H3('--Dataframe Ups(+) of: ' + timeframe))
        timeseries_list.append(h_.get_dash_table(dataframes_ups[timeframe], timeframe))

    return timeseries_list


def main():
    try:
        app.run_server(debug=True)
    except Exception as e:
        print(e)
        logging.info(e)


if __name__ == '__main__':
    main()
