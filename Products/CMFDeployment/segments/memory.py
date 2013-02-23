"""
Invoke garbage collector via periodic savepoint.
"""

import transaction
from core import PipeSegment

class SavepointGC(PipeSegment):

    def __init__(self):
        self._count = 0

    def process(self, pipe, content ):
        self._count += 1
        if self._count % 3000:
            transaction.savepoint()
        return content
        
