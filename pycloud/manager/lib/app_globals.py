"""The application's Globals object"""

from pylons import config
from pymongo import Connection
from pymongo.errors import ConnectionFailure

from pycloud import create_cloudlet

class Globals(object):

    """Globals acts as a container for objects available throughout the
    life of the application

    """

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'g' variable

        We will initialize our database connection here
        """

        # host = config['pycloud.mongo.host']
        # port = int(config['pycloud.mongo.port'])
        # db = config['pycloud.mongo.db']
        #
        # try:
        #     conn = Connection(host, port)
        # except ConnectionFailure as error:
        #     print error
        #     raise Exception('Unable to connect to MongoDB')

        self.cloudlet = create_cloudlet(config)