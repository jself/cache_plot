# Create your views here.
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse
import glob
import os
import md5
import gzip
import datetime
from pymongo.code import Code
import backend


def hit_ratio(hits, misses):
    if hits or misses:
        return hits/float((hits + misses))*100
    return "N/A"

def get_overall(tables):
    total_hits = 0
    total_misses = 0
    for table in tables.find():
        total_hits += table.get('hits', 0)
        total_misses += table.get('misses', 0)
    return hit_ratio(total_hits, total_misses)


def analyze(request):
    tables, requests = backend.get_buckets()

    overall = get_overall(tables)

    requests = list(requests.find())
    for i in requests:
        i['hits'] = i.get('hits', 0)
        i['misses'] = i.get('misses', 0)
        i['hit_ratio'] = hit_ratio(i['hits'], i['misses'])
        i['path'] = i['path'][0:100]

    def sort_worst(a, b):
        if a['hit_ratio'] == 'N/A':
            return 1
        if b['hit_ratio'] == 'N/A':
            return -1
        return cmp(a['hit_ratio'], b['hit_ratio'])
    def sort_best(a, b):
        if a['hit_ratio'] == 'N/A':
            return 1
        if b['hit_ratio'] == 'N/A':
            return -1
        return cmp(b['hit_ratio'], a['hit_ratio'])

    def table_sorter(a, b):
        return cmp(a['table'], b['table'])

    requests.sort(sort_best)
    best = list(requests[0:10])
    requests.sort(sort_worst)
    worst = list(requests[0:10])

    tables = list(tables.find())

    tables.sort(table_sorter)
    for table in tables:
        table['hits'] = table.get('hits', 0)
        table['misses'] = table.get('misses', 0)
        table['hit_ratio'] = hit_ratio(table['hits'], table['misses'])
        table['count'] = table['hits'] + table['misses']
    

    return render_to_response('analyze.html', dict(worst=worst, best=best, overall=overall, tables=tables))

