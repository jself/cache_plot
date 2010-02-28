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
    hits = tables.find({"result": "hit"}).count()
    misses = tables.find({"result":"miss"}).count()
    return hit_ratio(hits, misses)

def get_results(requests):
    filter = Code("""function (obj) {
        if (obj.hits > 0 or obj.misses > 0) {
            return true;
        }   return false;
    }""")
        
    reduce = Code("""function (obj, prev) {
        prev.hits += obj.hits;
        prev.misses += obj.misses;
        prev.called += 1;
    }""")
    return requests.group(['path'], filter, {'called':0, 'hits':0, 'misses':0}, reduce)

def table_results(tables):
    reduce = Code("""function (obj, prev) {
        if (obj.result == "hit") {
            prev.hits += 1
        }   else {
            prev.misses += 1
        }
            prev.count += 1;
        }""")
    return tables.group(['table'], None, {'hits':0, 'misses':0, 'count':0}, reduce)


def analyze(request):
    tables, request = backend.get_buckets()

    overall = get_overall(tables)

    requests = get_results(request)
    for i in requests:
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

    tables = table_results(tables)
    tables.sort(table_sorter)
    for table in tables:
        table['hit_ratio'] = hit_ratio(table['hits'], table['misses'])

    return render_to_response('analyze.html', dict(worst=worst, best=best, overall=overall, tables=tables))

