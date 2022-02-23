import loggingimport sysfrom datetime import datetime, timedeltasys.path.append('...')import plotly.graph_objects as go# import matplotlib.pyplot as pltimport numpy as npimport pandas as pdfrom pandas import DataFrame as dffrom config.config import timeframes, KPIS_path, ema_means_path, ema_medians_pathimport src.prepare_data as funcimport src.help_functions as h_def get_multilevel_dataframe(timeframes, main_timeframe, day_start, ONE_DAY=True):    # if ONE_DAY = true: calculate multilevel_dataframe for just given one day    multilevel_df = {}    dataframes = {}    for k in range(len(timeframes)):        current_timeframe = timeframes[k]['time']        if current_timeframe not in ("1m", "3m", "5m", "3d", "1w", "1M"):            if current_timeframe == main_timeframe:                multilevel_df = h_.cleanup_dataframe(timeframes[k], main_timeframe)                # for now: reset Index                multilevel_df["id"] = multilevel_df.index                multilevel_df = h_.filter_date(multilevel_df, day_start, ONE_DAY).reset_index(drop=True)            else:                current_df = h_.cleanup_dataframe(timeframes[k], main_timeframe)                current_df = h_.filter_date(current_df, day_start, ONE_DAY).reset_index(drop=True)                dataframes[current_timeframe] = current_df    for j in range(multilevel_df.shape[0]):        for i in range(len(timeframes)):            current_timeframe = timeframes[i]['time']            if current_timeframe not in ("1m", "3m", "5m", main_timeframe, "3d", "1w", "1M"):                current_df = dataframes[current_timeframe]                if current_timeframe == "30m":                    matched_date = (multilevel_df.loc[j, "date"]).ceil(freq="30min")                elif current_timeframe == "1h":                    matched_date = (multilevel_df.loc[j, "date"]).ceil(freq=current_timeframe)                elif current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d"):                    matched_date = ((multilevel_df.loc[j, "date"] - timedelta(hours=1)).ceil(                        freq=current_timeframe) + timedelta(hours=1))                WT_EMA_SMA_id_list = h_.get_WT_EMA_WT_SMA_of_dataframes(matched_date, current_df)                multilevel_df.loc[j, current_timeframe + "_WT_EMA"] = WT_EMA_SMA_id_list[0]                multilevel_df.loc[j, current_timeframe + "_WT_SMA"] = WT_EMA_SMA_id_list[1]                id_current_df_matched_row = WT_EMA_SMA_id_list[2]                if id_current_df_matched_row == 0:                    multilevel_df.loc[j, "id"] = 0    return multilevel_dfdef create_masterfile(main_timeframe, day_start):    # get_multilevel_dataframe(timeframes=timeframes, main_timeframe="15m", day_start=day_start)    multilevel_df = get_multilevel_dataframe(timeframes=timeframes, main_timeframe="15m", day_start=day_start,                                             ONE_DAY=False)    main_timeframe_master_filepath = ""    for i in range(len(timeframes)):        if timeframes[i]['time'] == main_timeframe:            main_timeframe_master_filepath = timeframes[i]['master_file']            print("\n--Success multilevel_dataframe for: " + main_timeframe)            multilevel_df.to_feather(main_timeframe_master_filepath)def update_masterfile(main_timeframe):    for i in range(len(timeframes)):        current_timeframe = timeframes[i]['time']        if current_timeframe == main_timeframe:            old_dataframe = pd.read_feather(timeframes[i]['master_file'])            last_row = np.nan            date_of_second_last_row = np.nan            for j in range(len(old_dataframe) - 1, -1, -1):                if not np.isnan(old_dataframe.loc[j, "1d_WT_EMA"]) and old_dataframe.loc[j, "id"] != 0:                    last_row = j - 1                    date_of_second_last_row = str(old_dataframe.loc[last_row - 1, "date"])                    break            old_dataframe = old_dataframe[:last_row]            new_dataframe = get_multilevel_dataframe(timeframes=timeframes, main_timeframe=main_timeframe,                                                     day_start=date_of_second_last_row, ONE_DAY=False)            merged_dataframe = pd.concat([old_dataframe, new_dataframe]).reset_index(drop=True)            merged_dataframe.to_feather(timeframes[i]['master_file'])            print("\n--Success multilevel_dataframe for: " + main_timeframe)# TODO merge_1def get_UPs_from_masterfile(main_timeframe):    for i in range(len(timeframes)):        if main_timeframe == timeframes[i]['time']:            current_df = pd.read_feather(timeframes[i]['master_file'])            up_df = container_df = current_df.head(0)            for j in range(current_df.shape[0]):                if current_df.loc[j, "WT_EMA"] > current_df.loc[j, "WT_SMA"]:                    current_df.loc[j, "WT_EMA>WT_SMA"] = True                else:                    current_df.loc[j, "WT_EMA>WT_SMA"] = False                if current_df.loc[j, "%_run_total"] >= 1:                    if j == current_df.shape[0] - 1:                        container_df = current_df.iloc[[j]]                    else:                        if current_df.loc[j + 1, "WT_EMA"] > current_df.loc[j + 1, "WT_SMA"]:                            current_df.loc[j + 1, "WT_EMA>WT_SMA"] = True                        else:                            current_df.loc[j + 1, "WT_EMA>WT_SMA"] = False                        container_df = pd.concat([current_df.iloc[[j]], current_df.iloc[[j + 1]]]).reset_index(                            drop=True)                    n = j                    while current_df.loc[n, 'up(+)_down(-)'] == "+":                        n -= 1                        if n < 0:                            break                        container_df = pd.concat([current_df.iloc[[n]], container_df]).reset_index(drop=True)                    up_df = pd.concat([up_df, container_df]).reset_index(drop=True)                    container_df = container_df.head(0)            up_df.to_feather(timeframes[i]['master_file_ups'])            print("\n--Success get_UPs(+)_from_masterfile for: " + main_timeframe)# TODO merge_2def get_boxplot(main_timeframe):    for i in range(len(timeframes)):        if main_timeframe == timeframes[i]['time']:            master_ups_df = pd.read_feather(timeframes[i]['master_file_ups'])            current_df = master_ups_df.head(0)            for j in range(0, master_ups_df.shape[0]):                if master_ups_df.loc[j, "up(+)_down(-)"] == "-" and not np.isnan(master_ups_df.loc[j, "%_run_total"]):                    current_row = master_ups_df.iloc[[j]]                    current_df = pd.concat([current_df, current_row]).reset_index(drop=True)            print(current_df)            EMA_columns = ["WT_EMA", "30m_WT_EMA", "1h_WT_EMA", "2h_WT_EMA", "4h_WT_EMA",                           "6h_WT_EMA", "8h_WT_EMA", "12h_WT_EMA", "1d_WT_EMA"]            SMA_columns = ["WT_SMA", "30m_WT_SMA", "1h_WT_SMA", "2h_WT_SMA", "4h_WT_SMA",                           "6h_WT_SMA", "8h_WT_SMA", "12h_WT_SMA", "1d_WT_SMA"]            columns = list(current_df)[6:]            columns.pop(2)            # boxplot = current_df.boxplot(column=columns)            # boxplot.plot()            boxplot1 = current_df.boxplot(column=EMA_columns)            boxplot1.plot()            plt.show()            boxplot2 = current_df.boxplot(column=SMA_columns)            boxplot2.plot()            plt.show()# TODO:merge_1def get_UPs_of_timeframes(day_start="2020-01-01 00:00:00"):    for i in range(len(timeframes)):        current_timeframe = timeframes[i]['time']        if current_timeframe not in ("1m", "3m", "5m", "15m"):            current_df = h_.cleanup_dataframe(timeframes[i], current_timeframe)            # if 'id' in current_df.columns:            # current_df.pop('id')            current_df = h_.filter_date(current_df, day_start).reset_index(drop=True)            up_df = container_df = current_df.head(0)            for j in range(0, current_df.shape[0]):                if current_df.loc[j, "WT_EMA"] > current_df.loc[j, "WT_SMA"]:                    current_df.loc[j, "WT_EMA>WT_SMA"] = True                else:                    current_df.loc[j, "WT_EMA>WT_SMA"] = False                if current_df.loc[j, "%_run_total"] >= 1:                    if j == current_df.shape[0] - 1:                        container_df = current_df.iloc[[j]]                    else:                        if current_df.loc[j + 1, "WT_EMA"] > current_df.loc[j + 1, "WT_SMA"]:                            current_df.loc[j + 1, "WT_EMA>WT_SMA"] = True                        else:                            current_df.loc[j + 1, "WT_EMA>WT_SMA"] = False                        container_df = pd.concat([current_df.iloc[[j]], current_df.iloc[[j + 1]]]).reset_index(                            drop=True)                    n = j                    while current_df.loc[n, 'up(+)_down(-)'] == "+":                        n -= 1                        if n < 0:                            break                        container_df = pd.concat([current_df.iloc[[n]], container_df]).reset_index(drop=True)                    up_df = pd.concat([up_df, container_df]).reset_index(drop=True)                    container_df = container_df.head(0)            up_df.to_feather(timeframes[i]['ups'])            print("\n--Success get_UPs(+) for: " + current_timeframe)# TODO merge_2def get_boxplot():    for i in range(len(timeframes)):        if timeframes[i]['time'] not in ("1m", "3m", "5m", "15m"):            ups_df = pd.read_feather(timeframes[i]['ups'])            current_df = ups_df.head(0)            for j in range(0, ups_df.shape[0]):                if ups_df.loc[j, "up(+)_down(-)"] == "-" and not np.isnan(ups_df.loc[j, "%_run_total"]):                    current_row = ups_df.iloc[[j]]                    current_df = pd.concat([current_df, current_row]).reset_index(drop=True)            # print(current_df)            columns = ["WT_EMA", "WT_SMA"]            boxplot = current_df.boxplot(column=columns)            plt.title(timeframes[i]['time'])            boxplot.plot()            plt.show()def get_last_row_runs_of_master(main_timeframe):    last_two_runs_df = {}    cols = ["close", "HA_close", "%of_run", "%_run_total", "WT_EMA", "WT_SMA",            "30m_WT_EMA", "1h_WT_EMA", "2h_WT_EMA", "4h_WT_EMA", "6h_WT_EMA", "8h_WT_EMA", "12h_WT_EMA", "1d_WT_EMA",            "30m_WT_SMA", "1h_WT_SMA", "2h_WT_SMA", "4h_WT_SMA", "6h_WT_SMA", "8h_WT_SMA", "12h_WT_SMA", "1d_WT_SMA"]    for i in range(len(timeframes)):        current_timeframe = timeframes[i]['time']        if current_timeframe == main_timeframe:            current_df = pd.read_feather(timeframes[i]['master_file'])            last_row = counter = 0            for j in range(len(current_df) - 1, -1, -1):                if not np.isnan(current_df.loc[j, "%_run_total"]):                    counter += 1                    if counter == 4:                        last_row = j                        break            last_two_runs_df = current_df[last_row:].sort_index(ascending=False)            last_two_runs_df[cols] = last_two_runs_df[cols].round(2)    return last_two_runs_dfdef create_nested_bar_chart():    day_before_yesterday = datetime.now() - timedelta(days=2)    day_before_yesterday = str(day_before_yesterday.year) + "-" + str(day_before_yesterday.month) + "-" + str(        day_before_yesterday.day) + " 00:00:00"    day_before_yesterday = datetime.strptime(day_before_yesterday, '%Y-%m-%d %H:%M:%S')    yesterday = day_before_yesterday + timedelta(days=1)    today = yesterday + timedelta(days=1)    fig_3days = go.Figure()    fig_today = go.Figure()    fig_yesterday = go.Figure()    fig_day_before_yesterday = go.Figure()    for i in range(len(timeframes)):        current_timeframe = timeframes[i]['time']        if current_timeframe not in ("1m", "3m", "5m", "1w", "1M", "3d"):            # if current_timeframe in ("1h", "2h", "4h", "6h", "8h", "12h", "1d"):            current_df = h_.filter_date(h_.cleanup_dataframe(timeframes[i], current_timeframe),                                        str(day_before_yesterday)).reset_index(                drop=True)            df_today = current_df[current_df.date.between(today, (today + timedelta(days=1)))].reset_index(drop=True)            df_yesterday = current_df[current_df.date.between(yesterday, (yesterday + timedelta(days=1)))].reset_index(                drop=True)            df_day_before_yesterday = current_df[                current_df.date.between(day_before_yesterday, (day_before_yesterday + timedelta(days=1)))].reset_index(                drop=True)            """            for j in range(0, df_day_before_yesterday.shape[0]):                if df_day_before_yesterday.loc[j, "up(+)_down(-)"] == "+":                    Long_Short = 'long'                if df_day_before_yesterday.loc[j, "up(+)_down(-)"] == "-":                    Long_Short = 'short'                if current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d") and j == 0:                    fig_day_before_yesterday.add_trace(h_.get_fig(current_timeframe, Long_Short, "first"))                else:                    fig_day_before_yesterday.add_trace(h_.get_fig(current_timeframe, Long_Short))                if current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d") and j == df_day_before_yesterday.shape[0] - 1:                    if df_yesterday.loc[0, "up(+)_down(-)"] == "+":                        Long_Short = 'long'                    if df_yesterday.loc[0, "up(+)_down(-)"] == "-":                        Long_Short = 'short'                    fig_day_before_yesterday.add_trace(h_.get_fig(current_timeframe, Long_Short, "last"))            for j in range(0, df_yesterday.shape[0]):                if df_yesterday.loc[j, "up(+)_down(-)"] == "+":                    Long_Short = 'long'                if df_yesterday.loc[j, "up(+)_down(-)"] == "-":                    Long_Short = 'short'                if current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d") and j == 0:                    fig_yesterday.add_trace(h_.get_fig(current_timeframe, Long_Short, "first"))                elif current_timeframe in ("15m", "30m", "1h") and j == 0:                    "skip"                else:                    fig_yesterday.add_trace(h_.get_fig(current_timeframe, Long_Short))                if current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d") and j == df_yesterday.shape[0] - 1:                    if df_today.loc[0, "up(+)_down(-)"] == "+":                        Long_Short = 'long'                    if df_today.loc[0, "up(+)_down(-)"] == "-":                        Long_Short = 'short'                    fig_yesterday.add_trace(h_.get_fig(current_timeframe, Long_Short, "last"))            for j in range(0, df_today.shape[0]):                if df_today.loc[j, "up(+)_down(-)"] == "+":                    Long_Short = 'long'                if df_today.loc[j, "up(+)_down(-)"] == "-":                    Long_Short = 'short'                if current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d") and j == 0:                    fig_today.add_trace(h_.get_fig(current_timeframe, Long_Short, "first"))                elif current_timeframe in ("15m", "30m", "1h") and j == 0:                    "skip"                else:                    fig_today.add_trace(h_.get_fig(current_timeframe, Long_Short))                if current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d") and j == df_today.shape[0] - 1:                    fig_today.add_trace(h_.get_fig(current_timeframe, "black", "last"))            """            for j in range(0, current_df.shape[0]):                if current_df.loc[j, "up(+)_down(-)"] == "+":                    Long_Short = 'long'                if current_df.loc[j, "up(+)_down(-)"] == "-":                    Long_Short = 'short'                if current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d") and j == 0:                    fig_3days.add_trace(h_.get_fig(current_timeframe, Long_Short, "first"))                else:                    fig_3days.add_trace(h_.get_fig(current_timeframe, Long_Short))                # if current_timeframe in ("2h", "4h", "6h", "8h", "12h", "1d") and j == current_df.shape[0] - 1:                # fig_3days.add_trace(h_.get_fig(current_timeframe, "black", "last"))    # fig_day_before_yesterday.update_layout(barmode='stack', title="BTC timeframes DAY BEFORE YESTERDAY", showlegend=False)    # fig_day_before_yesterday.show()    # ig_yesterday.update_layout(barmode='stack', title="BTC timeframes YESTERDAY", showlegend=False)    # fig_yesterday.show()    # fig_today.update_layout(barmode='stack', title="BTC timeframes TODAY", showlegend=False)    # fig_today.show()    fig_3days.update_layout(barmode='stack', title="BTC timeframes for 3 Days", showlegend=False)    # fig_3days.show()    return fig_3daysdef create_KPIs_df(days=0, SHOW_PERCENT=False):    if days == 0:        day_start = ""    else:        day_start = datetime.now() - timedelta(days=days)        day_start = str(day_start.year) + "-" + str(day_start.month) + "-" + str(day_start.day) + " 00:00:00"    KPIs_df = df([], columns=['filter']).reset_index(drop=True)    columns_list = ["15m", '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']    # columns_list = ['6h', '8h', '12h', '1d', '3d', '1w', '1M']    filter_1 = "sum: #F1"    filter_2_1 = "WT_EMA>WT_SMA_TRUE: #F2_1"    filter_2_2 = "WT_EMA>WT_SMA_FALSE: #F2_2"    filter_3_1 = "up(+) & F2_1: #F3_1"    filter_3_2 = "up(+) & F2_2: #F3_2"    filter_4_1 = "run_start(n-1) & F2_1: #F4_1"    filter_4_2 = "run_start(n-1) & F2_2: #F4_2"    filter_5_1 = "run_end(n+1) & F2_1: #F5_1"    filter_5_2 = "run_end(n+1) & F2_2: #F5_2"    filter_list = [filter_1, filter_2_1, filter_2_2, filter_3_1, filter_3_2,                   filter_4_1, filter_4_2, filter_5_1, filter_5_2]    EMA_list = []    for row in range(len(filter_list)):        KPIs_df.loc[row, "filter"] = filter_list[row]        EMA_list.append([])        for column in columns_list:            KPIs_df.loc[row, column] = 0            if row != 0:                EMA_list[row].append([])    for i in range(len(timeframes)):        current_timeframe = timeframes[i]['time']        if current_timeframe in columns_list:            if current_timeframe == "15m":                current_df = pd.read_feather(timeframes[i]['master_file_ups'])            else:                current_df = pd.read_feather(timeframes[i]['ups'])            if day_start != "":                current_df = h_.filter_date(current_df, day_start).reset_index(drop=True)            # 1. Filter            KPIs_df.loc[filter_list.index(filter_1), current_timeframe] = current_df.shape[0]            EMA_list[filter_list.index(filter_1)].append([current_timeframe])            current_column_nr = i - (len(timeframes) - len(columns_list))            for j in range(current_df.shape[0]):                if current_df.loc[j, "id"] != 0 and j > 0:                    current_wt_ema = current_df.loc[j, "WT_EMA"].round(2)                    # 2. Filter all                    if current_df.loc[j, "WT_EMA>WT_SMA"]:                        KPIs_df.loc[filter_list.index(filter_2_1), current_timeframe] += 1                        EMA_list[filter_list.index(filter_2_1)][current_column_nr].append(current_wt_ema)                    else:                        KPIs_df.loc[filter_list.index(filter_2_2), current_timeframe] += 1                        EMA_list[filter_list.index(filter_2_2)][current_column_nr].append(current_wt_ema)                    # 3. Filter run                    if current_df.loc[j, "WT_EMA>WT_SMA"] and current_df.loc[j, "up(+)_down(-)"] == "+" \                            and current_df.loc[(j - 1), "up(+)_down(-)"] == "-":                        KPIs_df.loc[filter_list.index(filter_3_1), current_timeframe] += 1                        EMA_list[filter_list.index(filter_3_1)][current_column_nr].append(current_wt_ema)                    elif not current_df.loc[j, "WT_EMA>WT_SMA"] and current_df.loc[j, "up(+)_down(-)"] == "+" \                            and current_df.loc[(j - 1), "up(+)_down(-)"] == "-":                        KPIs_df.loc[filter_list.index(filter_3_2), current_timeframe] += 1                        EMA_list[filter_list.index(filter_3_2)][current_column_nr].append(current_wt_ema)                    # 4. Filter run_start                    if current_df.loc[j, "WT_EMA>WT_SMA"] and current_df.loc[j, "up(+)_down(-)"] == "-" \                            and not np.isnan(current_df.loc[j, "%_run_total"]):                        KPIs_df.loc[filter_list.index(filter_4_1), current_timeframe] += 1                        EMA_list[filter_list.index(filter_4_1)][current_column_nr].append(current_wt_ema)                    elif not current_df.loc[j, "WT_EMA>WT_SMA"] and current_df.loc[j, "up(+)_down(-)"] == "-" \                            and not np.isnan(current_df.loc[j, "%_run_total"]):                        KPIs_df.loc[filter_list.index(filter_4_2), current_timeframe] += 1                        EMA_list[filter_list.index(filter_4_2)][current_column_nr].append(current_wt_ema)                    # 5. Filter run_end                    if current_df.loc[j, "WT_EMA>WT_SMA"] and current_df.loc[j, "up(+)_down(-)"] == "-" \                            and np.isnan(current_df.loc[j, "%_run_total"]):                        KPIs_df.loc[filter_list.index(filter_5_1), current_timeframe] += 1                        EMA_list[filter_list.index(filter_5_1)][current_column_nr].append(current_wt_ema)                    elif not current_df.loc[j, "WT_EMA>WT_SMA"] and current_df.loc[j, "up(+)_down(-)"] == "-" \                            and np.isnan(current_df.loc[j, "%_run_total"]):                        KPIs_df.loc[filter_list.index(filter_5_2), current_timeframe] += 1                        EMA_list[filter_list.index(filter_5_2)][current_column_nr].append(current_wt_ema)    if day_start == "":        KPIs_df.to_feather(KPIS_path)        create_mean_median_df(EMA_list, KPIs_df)        print("\n--Success calculate KPIs: ")    if SHOW_PERCENT:        print("#################################Days:", days)        get_KPIs_df_percent(KPIs_df)    return KPIs_dfdef create_mean_median_df(ema_list, KPIs_df):    ema_means_df = df()    ema_median_df = df()    for row_i in range(KPIs_df.shape[0]):        if row_i != 0:            for column_i in range((len(KPIs_df.columns))):                if column_i == 0:                    ema_means_df.loc[row_i, "filter"] = KPIs_df.loc[row_i, "filter"]                    ema_median_df.loc[row_i, "filter"] = KPIs_df.loc[row_i, "filter"]                else:                    current_element = ema_list[row_i][column_i - 1]                    if current_element:                        ema_means_df.loc[row_i, KPIs_df.columns[column_i]] = np.mean(current_element).round(2)                        ema_median_df.loc[row_i, KPIs_df.columns[column_i]] = np.median(current_element).round(2)    ema_means_df.reset_index(drop=True).to_feather(ema_means_path)    ema_median_df.reset_index(drop=True).to_feather(ema_medians_path)def get_KPIs_df_percent(KPIs_df):    KPIs_df_percent = df()    KPIs_df_percent["filter"] = KPIs_df["filter"]    for i in range(0, KPIs_df.shape[0]):        for j in range(len(timeframes)):            timeframe = timeframes[j]['time']            if timeframe in ["15m", '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']:                if i == 0 or KPIs_df.loc[i, timeframe] == 0:                    KPIs_df_percent.loc[i, timeframe] = KPIs_df.loc[i, timeframe]                elif i == 1 or i == 2:                    KPIs_df_percent.loc[i, timeframe] = (                            KPIs_df.loc[i, timeframe] / KPIs_df.loc[0, timeframe] * 100).round(2)                else:                    if i % 2:                        KPIs_df_percent.loc[i, timeframe] = (KPIs_df.loc[i, timeframe] * 100 / (                                KPIs_df.loc[i, timeframe] + KPIs_df.loc[i + 1, timeframe])).round(2)                    else:                        KPIs_df_percent.loc[i, timeframe] = (KPIs_df.loc[i, timeframe] * 100 / (                                KPIs_df.loc[i, timeframe] + KPIs_df.loc[i - 1, timeframe])).round(2)    # print("KPIs df: ")    # print(KPIs_df)    # print("\nKPIs df in Percent: ")    # print(KPIs_df_percent)    return KPIs_df_percent# TODO:def merge_KPIsDF_mean_median():    KPIs_df = get_KPIs_df_percent(pd.read_feather(KPIS_path))    means_df = pd.read_feather(ema_means_path)    medians_df = pd.read_feather(ema_medians_path)    merged_df = df({"stage": ["run_start", "", "", "run", "", "", "run_end", "", ""],                    "kind": ["%", "mean", "median", "%", "mean", "median", "%", "mean", "median"]})    true = "_T"    false = "_F"    cols = KPIs_df.columns[1:]    for i in range(KPIs_df.shape[0]):        for col in cols:            # run_start            if i == 0 and merged_df.loc[i, "kind"] == "%":                merged_df.loc[i, col + true] = KPIs_df.loc[5, col]                merged_df.loc[i, col + false] = KPIs_df.loc[6, col]            elif i == 1 and merged_df.loc[i, "kind"] == "mean":                merged_df.loc[i, col + true] = means_df.loc[4, col]                merged_df.loc[i, col + false] = means_df.loc[5, col]            elif i == 2 and merged_df.loc[i, "kind"] == "median":                merged_df.loc[i, col + true] = medians_df.loc[4, col]                merged_df.loc[i, col + false] = medians_df.loc[5, col]            # run            elif i == 3 and merged_df.loc[i, "kind"] == "%":                merged_df.loc[i, col + true] = KPIs_df.loc[3, col]                merged_df.loc[i, col + false] = KPIs_df.loc[4, col]            elif i == 4 and merged_df.loc[i, "kind"] == "mean":                merged_df.loc[i, col + true] = means_df.loc[2, col]                merged_df.loc[i, col + false] = means_df.loc[3, col]            elif i == 5 and merged_df.loc[i, "kind"] == "median":                merged_df.loc[i, col + true] = medians_df.loc[2, col]                merged_df.loc[i, col + false] = medians_df.loc[3, col]            # runend            elif i == 6 and merged_df.loc[i, "kind"] == "%":                merged_df.loc[i, col + true] = KPIs_df.loc[7, col]                merged_df.loc[i, col + false] = KPIs_df.loc[8, col]            elif i == 7 and merged_df.loc[i, "kind"] == "mean":                merged_df.loc[i, col + true] = means_df.loc[6, col]                merged_df.loc[i, col + false] = means_df.loc[7, col]            elif i == 8 and merged_df.loc[i, "kind"] == "median":                merged_df.loc[i, col + true] = medians_df.loc[6, col]                merged_df.loc[i, col + false] = medians_df.loc[7, col]    return merged_dfdef main():    try:        pd.set_option('expand_frame_repr', False)        pd.set_option('display.max_rows', 100)        # current_df = get_last_row_runs_of_master("15m")        # print(current_df)        # create_nested_bar_chart()        # get_UPs_of_timeframes()        create_KPIs_df(days=0, SHOW_PERCENT=False)        #KPIs_df = pd.read_feather(KPIS_path)        #print(KPIs_df)        print("\nKPIs df in Percent: ")        # print(get_KPIs_df_percent(KPIs_df))        """        for i in range(len(timeframes)):            current_timeframe = timeframes[i]['time']            if current_timeframe == "2h":                current_df = h_.cleanup_dataframe(timeframes[i], current_timeframe)                print(current_df.tail(100))        """    except Exception as e:        print(e)        logging.info(e)if __name__ == '__main__':    main()