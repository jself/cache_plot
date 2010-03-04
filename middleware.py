from django.conf import settings
from johnny import signals
import uuid
import time
import backend
import datetime

def get_unix_date():
    #no reason to use int here other than that it's just as easy as storing a datetime...
    #dates are not accepted in couch db
    return int(datetime.datetime.now().date().strftime('%s'))

class CachePlotMiddleware(object):
    def __init__(self):
        signals.qc_hit.connect(self._hit)
        signals.qc_miss.connect(self._miss)

        try:
            self.tables, self.requests = backend.get_buckets()
        except:
            pass

    def _hit(self, sender, **kwargs):
        tables = kwargs['tables']
        for table in tables:
            try:
                self.tables.update({"table":table}, 
                                   {"$inc":{"hits":1}}, True)

            except Exception, e:
                print "Error when logging row to tables: " %str(e)
        self.log_row['hits'] += 1
            
    def _miss(self, sender, **kwargs):
        tables = kwargs['tables']
        for table in tables:
            try:
                self.tables.update({"table":table}, {"$inc":{"misses":1}}, True)
                #self.tables.insert({'result':'miss',
                #                    'table':table,
                #                    'time':time.time()})
            except Exception, e:
                print "Error when logging row to tables: " %str(e)
        self.log_row['misses'] += 1


    def process_request(self, request):    
        req_id = str(uuid.uuid4())
        self.log_row = {}
        self.log_row['time'] = time.time()
        self.log_row['path'] = request.get_full_path()
        self.log_row['hits'] = 0
        self.log_row['misses'] = 0


    def log(self):
        try:
            self.requests.update({"path":self.log_row['path']},
                                 {"$inc":{"hits":self.log_row['hits'], "misses":self.log_row['misses'], 'visits':1}},
                                 True)
        except Exception, e:
            print "Error when logging row to requests: " %str(e)
    def process_response(self, request, response):
        self.log()
        return response

    def process_exception(self, request, exception):
        self.log()
