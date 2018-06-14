# TwistedTwoTimes
### A basic twisted client with two server connections  

This client uses the asynchronous, event driven networking engine [Twisted](https://twistedmatrix.com/trac/).

When I was learning twisted I could not find any examples of a client that opens two TCP connections to a single server. This serves as a simple code example of such a client. One connection is used for control and the other data receptions. The control is a bidirectional protcol using the built-in LineReceiver protocol. The data reciever starts on launch and waits on the specified port.  

This code was the basis for a much larger client.

