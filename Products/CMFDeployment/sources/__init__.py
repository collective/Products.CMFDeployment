"""
$Id: __init__.py 1177 2006-02-23 19:40:44Z hazmat $
"""

import catalog
import deletion
import dependency

try:
    import topic
except ImportError:
    topic = None
    
    print "Need ZMITopic Product for Topic Source"
