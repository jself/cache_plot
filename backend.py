from django.conf import settings
import pymongo
import datetime

def get_buckets():
    host = getattr(settings, 'CACHE_PLOT_HOST', 'localhost')
    port = getattr(settings, 'CACHE_PLOT_PORT', 27017)
    db = getattr(settings, 'CACHE_PLOT_DB', 'cache_plot')
    table_bucket = getattr(settings, 'CACHE_PLOT_TABLE_BUCKET', 'tables_aggr')
    request_bucket = getattr(settings, 'CACHE_PLOT_REQUEST_BUCKET', 'requests_aggr')

    con = pymongo.Connection(host, port)
    db = con[db]
    tables = db[table_bucket]
    request = db[request_bucket]
    return (tables, request)

