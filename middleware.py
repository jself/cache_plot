from django.conf import settings
from johnny import signals
import uuid
import time
import backend

class CachePlotMiddleware(object):
    def __init__(self):
        signals.qc_hit.connect(self._hit)
        signals.qc_miss.connect(self._miss)

        self.tables, self.requests = backend.get_buckets()

    def _hit(self, sender, **kwargs):
        tables = kwargs['tables']
        for table in tables:
            self.tables.insert({'result':'hit',
                                'table':table,
                                'time':time.time()})
        self.log_row['hits'] += 1
            
    def _miss(self, sender, **kwargs):
        tables = kwargs['tables']
        for table in tables:
            self.tables.insert({'result':'miss',
                                'table':table,
                                'time':time.time()})
        self.log_row['misses'] += 1


    def process_request(self, request):    
        req_id = str(uuid.uuid4())
        self.log_row = {}
        self.log_row['time'] = time.time()
        self.log_row['path'] = request.get_full_path()
        self.log_row['hits'] = 0
        self.log_row['misses'] = 0


    def process_response(self, request, response):
        self.requests.insert(self.log_row)
        return response

    def process_exception(self, request, exception):
        self.requests.insert(self.log_row)
