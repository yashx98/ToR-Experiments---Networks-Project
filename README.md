This is the repo for the project of Networks and Mobile Systems course.


Multiple measurements to get mean and variance. Caching effects?
Removing caching effects when running multiple measurements? Parallelize?


__DisablePredictedCircuits  --> If true, Tor will not launch preemptive "general-purpose" circuits for
    streams to attach to.  (It will still launch circuits for testing and
    for hidden services.)










1. sudo apt update
2. sudo apt install tor
3. In /etc/tor/torrc, add line SocksPort 9200
4. sudo apt install python3-pip
5. pip install stem
6. git clone https://gitlab.torproject.org/tpo/core/tor.git
7. Change hops by changing DEFAULT_ROUTE_LEN in file src/core/or/or.h
8. To build Tor: 
  Initial: sudo apt-get install libevent-dev
  sudo apt install asciidoc
  1. ./autogen.sh
  2. ./configure
  3. make
  4. make install
9. To login in the control plane:
  telnet localhost 9201, then authenticate
10.
