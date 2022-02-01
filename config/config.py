# if True run testing code and if False run real code
DRYRUN = False
coin = 'BTCUSDT'
path = '/.../Project_name/data/'

KPIS_path = path + "kpis.feather"
ema_means_path = path + "ema_means_ups_path.feather"
ema_medians_path = path + "ema_medians_ups_path.feather"


timeframes = [{
    'time': "1h",  # client.KLINE_INTERVAL_1HOUR,
    'file': path + '1h.feather'
}]

if DRYRUN:
    timeframes = timeframes

else:
    timeframes = [{
        'time': "1m",  # client.KLINE_INTERVAL_1MINUTE
        'file': path + '1min.feather',
        'ups': path + '1min_ups.feather'
    }, {
        'time': "3m",  # client.KLINE_INTERVAL_3MINUTE,
        'file': path + '3min.feather',
        'ups': path + '3min_ups.feather'
    }, {
        'time': "5m",  # client.KLINE_INTERVAL_5MINUTE,
        'file': path + '5min.feather',
        'ups': path + '5min_ups.feather'
    }, {
        'time': "15m",  # client.KLINE_INTERVAL_15MINUTE,
        'file': path + '15min.feather',
        'master_file': path + '15min_master.feather',
        'master_file_ups': path + '15min_master_ups.feather'
    }, {
        'time': "30m",  # client.KLINE_INTERVAL_30MINUTE,
        'file': path + '30min.feather',
        'ups': path + '30min_ups.feather'
    }, {
        'time': "1h",  # client.KLINE_INTERVAL_1HOUR,
        'file': path + '1h.feather',
        'ups': path + '1h_ups.feather'
    }, {
        'time': "2h",  # client.KLINE_INTERVAL_2HOUR,
        'file': path + '2h.feather',
        'ups': path + '2h_ups.feather'
    }, {
        'time': "4h",  # client.KLINE_INTERVAL_4HOUR,
        'file': path + '4h.feather',
        'ups': path + '4h_ups.feather'
    }, {
        'time': "6h",  # client.KLINE_INTERVAL_6HOUR,
        'file': path + '6h.feather',
        'ups': path + '6h_ups.feather'
    }, {
        'time': "8h",  # client.KLINE_INTERVAL_8HOUR,
        'file': path + '8h.feather',
        'ups': path + '8h_ups.feather'
    }, {
        'time': "12h",  # client.KLINE_INTERVAL_12HOUR,
        'file': path + '12h.feather',
        'ups': path + '12h_ups.feather'
    }, {
        'time': "1d",  # client.KLINE_INTERVAL_1DAY,
        'file': path + '1d.feather',
        'ups': path + '1d_ups.feather'
    }, {
        'time': "3d",  # client.KLINE_INTERVAL_3DAY,
        'file': path + '3d.feather',
        'ups': path + '3d_ups.feather'
    }, {
        'time': "1w",  # client.KLINE_INTERVAL_1WEEK,
        'file': path + '1week.feather',
        'ups': path + '1week_ups.feather'
    }, {
        'time': "1M",  # client.KLINE_INTERVAL_1MONTH,
        'file': path + '1month.feather',
        'ups': path + '1month_ups.feather'
    }]
