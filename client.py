import time
from twisted.python import failure
from twisted.internet import reactor, defer, task
from twisted.internet.protocol import Protocol
from twisted.internet import task
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver


class ControlProtocol(LineReceiver):  

    """ Uses built-in LineReceiver protocol to create the attributes for the control connection
    """ 
    def connectionMade(self):
        authCommands = ['Auth 123456','START'] # List of commands to send when a connection made. Good for Authentication.
        for command in authCommands:
            self.sendLine(command)

    def lineReceive(self, data):
        print(line) # This will not work, placeholder for now

class ControlProtocolFactory(ClientFactory):
    protocol = ControlProtocol

    def __init__(self):
        self.done = Deferred()

    def clientConnectionFailed(self, connector, reason):
        print('Connection with server failed:', reason.getErrorMessage())
        self.done.callback(reason)

    def clientConnectionLost(self,connector, reason):
        print('Connection with server lost:', reason.getErrorMeaage())
        self.done.callback(None)

class DataReceiverProtocol(Protocol):
    
    def __init__(self):
        self._request_id = 0

    def connectionMade(self):
        print "Connection made with server"

    def connectionLost(self, reason):
        print "Connection with server lost: %s" % reason.value

    def dataReceived(self, data):
        for message in data.split('\n'): 
            self._dump_to_disk(message.strip()) # split lines 

    def _dump_to_disk(self, message):
        
        # Placeholder for handleing datastream. Currently sends lines to stdio
        if not message:
            return
        try:
            print 'Receieved message:' % message
        except Exception as e:
            print 'error:', e, "while printing message to screen", repr(message)
 
    def _get_message_succeeded(self, result, request_id):
        """ On successful image receive print message stats
        """
        print("TODO image receive stats\n")

    def _get_massage_failed(self, failure, request_id):
        """ Error handleing for message 
        """
        print "[%i] Request failed: %s" % (request_id, failure.value)
        print("TODO: message receive failure message")
        
    # Cleanly close connection on server quit
    handle_QUIT = lambda self, *_: self.transport.loseConnection()


class DataReceiverSchedulingHandlers(object):

    # Could be handy in future if we run into timing problems

    def handle_SLEEP(self, seconds, result=None):
        result = result or 'Slept for %s seconds' % seconds
        deferred = defer.Deferred()
        reactor.callLater(float(seconds), deferred.callback, result)
        return deferred

    def handle_BLOCK(self, seconds, result=None):
        time.sleep(float(seconds))
        return defer.succeed(result or 'Blocked for %s seconds' % seconds)


if __name__ == '__main__':
    import sys 
    import time
    import socket
    from twisted.internet import threads
    from twisted.internet import reactor
    from twisted.internet.endpoints import serverFromString
    from twisted.internet.protocol import Protocol, ServerFactory
   
    IpAddress = 'localhost' # Server IP 
    controlPort = 12222 
    dataPort = 19999
    
    # Create data receiver listener object from string 
    server = serverFromString(reactor, 'tcp:%i' % dataPort)

    # Make data receiver to connect to ilt via mixins 
    class DataReceiver(DataReceiverProtocol, DataReceiverSchedulingHandlers):
        pass

    # TODO error checking to find out if image reciever is running
    # Start image receiver 
    server_factory = ServerFactory()
    server_factory.protocol = DataReceiver 
    server_factory.stopFactory = reactor.stop
    server_listen_deferred = server.listen(server_factory)

    # Set up control connection 
    ControlFactory = ControlProtocolFactory()
    reactor.connectTCP('localhost', 12222 , ControlFactory)

    @server_listen_deferred.addErrback
    def server_listen_failed(failure):
        # On failture to start server stop reactor
        print failure.value
        reactor.stop()

    @server_listen_deferred.addCallback
    def server_listen_callback(twisted_port):
        
        print "Listening on", twisted_port.getHost().imageRecPort

    # Start the reactor 
    reactor.run()
