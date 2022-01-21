import sys

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table

from config.config import timeframes
from dash.dependencies import Input, Output

master_ups_df = pd.read_feather(timeframes[3]['master_file_ups'])
master_ups_df['index'] = master_ups_df.index
master_ups_df.set_index('index', inplace=True, drop=False)
cols = ["close", "HA_close", "%of_run", "%_run_total", "WT_EMA", "WT_SMA",
        "30m_WT_EMA", "1h_WT_EMA", "2h_WT_EMA", "4h_WT_EMA", "6h_WT_EMA", "8h_WT_EMA", "12h_WT_EMA", "1d_WT_EMA",
        "30m_WT_SMA", "1h_WT_SMA", "2h_WT_SMA", "4h_WT_SMA", "6h_WT_SMA", "8h_WT_SMA", "12h_WT_SMA", "1d_WT_SMA"]
master_ups_df[cols] = master_ups_df[cols].round(2)

dataframes = {}
timeframe_list = []  # ['30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d']
for i in range(len(timeframes)):
    current_timeframe = timeframes[i]['time']
    if current_timeframe not in ("1m", "3m", "5m", "15m", "3d", "1w", "1M"):
        timeframe_list.append(current_timeframe)

        current_df = pd.read_feather(timeframes[i]['ups'])
        current_df['index'] = current_df.index
        current_df.set_index('index', inplace=True, drop=False)
        cols = ["close", "HA_close", "%of_run", "%_run_total", "WT_EMA", "WT_SMA"]
        current_df[cols] = current_df[cols].round(2)

        dataframes[current_timeframe] = current_df


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
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="multi",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell={'minWidth': '140px', 'maxWidth': '140px', 'width': '140px'},
        style_cell_conditional=[{
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in ['date']],
        style_data={'whiteSpace': 'normal', 'height': 'auto'},
        fill_width=False
    )


def create_children_list():
    children = []

    children.append(
        html.H1(
            children='My Dashboard',
            style={
                'textAlign': 'center',
                'color': '#7FDBFF'
            }))
    children.append(html.H3('Dataframe for masterfile - ups:'))
    children.append(get_dash_table(master_ups_df, "master_ups"))

    for i in range(len(timeframe_list)):
        children.append(html.Br())
        children.append(html.H3('--Dataframe for: ' + timeframe_list[i]))
        children.append(get_dash_table(dataframes[timeframe_list[i]], timeframe_list[i]))

    children.append(html.Br())
    children.append(html.Br())
    children.append(html.Div(id='#1-container'))
    children.append(html.Div(id='#2-container'))

    return children


# -------------------------------------------------------------------------------------
app = dash.Dash(__name__, prevent_initial_callbacks=True)

# See --> (https://dash.plotly.com/datatable/filtering)
app.layout = html.Div(children=create_children_list())


def main():
    try:
        app.run_server(debug=True)

    except Exception as e:
        print(e)
        logging.info(e)


if __name__ == '__main__':
    main()
