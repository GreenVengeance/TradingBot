# if True run testing code and if False run real code
DRYRUN = False
coin = 'BTCUSDT'
path = '/YOUR/PATH/OF/PROJECTFOLDER/data/'

timeframes = [{
    'time': "1h",  # client.KLINE_INTERVAL_1HOUR,
    'file': path + '1h.feather'
}]

if DRYRUN:
    timeframes = timeframes

else:
    timeframes = [{
        'time': "1m",  # client.KLINE_INTERVAL_1MINUTE
        'file': path + '1min.feather'
    }, {
        'time': "3m",  # client.KLINE_INTERVAL_3MINUTE,
        'file': path + '3min.feather'
    }, {
        'time': "5m",  # client.KLINE_INTERVAL_5MINUTE,
        'file': path + '5min.feather'
    }, {
        'time': "15m",  # client.KLINE_INTERVAL_15MINUTE,
        'file': path + '15min.feather',
        'master_file': path + '15min_master.feather'
    }, {
        'time': "30m",  # client.KLINE_INTERVAL_30MINUTE,
        'file': path + '30min.feather'
    }, {
        'time': "1h",  # client.KLINE_INTERVAL_1HOUR,
        'file': path + '1h.feather'
    }, {
        'time': "2h",  # client.KLINE_INTERVAL_2HOUR,
        'file': path + '2h.feather'
    }, {
        'time': "4h",  # client.KLINE_INTERVAL_4HOUR,
        'file': path + '4h.feather'
    }, {
        'time': "6h",  # client.KLINE_INTERVAL_6HOUR,
        'file': path + '6h.feather'
    }, {
        'time': "8h",  # client.KLINE_INTERVAL_8HOUR,
        'file': path + '8h.feather'
    }, {
        'time': "12h",  # client.KLINE_INTERVAL_12HOUR,
        'file': path + '12h.feather'
    }, {
        'time': "1d",  # client.KLINE_INTERVAL_1DAY,
        'file': path + '1d.feather'
    }, {
        'time': "3d",  # client.KLINE_INTERVAL_3DAY,
        'file': path + '3d.feather'
    }, {
        'time': "1w",  # client.KLINE_INTERVAL_1WEEK,
        'file': path + '1week.feather'
    }, {
        'time': "1M",  # client.KLINE_INTERVAL_1MONTH,
        'file': path + '1month.feather'
    }]
