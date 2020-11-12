#!/usr/bin/env python3
import argparse
import logging as log
import sys
from gbn_protocol import *

DEFAULT_PORT = 12345

def run_server(args, file):
    if args.rudp == 2:
        server_GBN_rudp(args.host, args.port, file)


def run_client(args, file):
    if args.rudp == 2:
        client_GBN_rudp(args.host, args.port, file)
    

def main():
    parser = argparse.ArgumentParser(description="netster")
    parser.add_argument('-p', '--port', type=str, default=DEFAULT_PORT,
                        help='listen on/connect to port <port> (default={}'
                        .format(DEFAULT_PORT))
    parser.add_argument('-i', '--iface', type=str, default='0.0.0.0',
                        help='listen on interface <dev>')
    parser.add_argument('-f', '--file', type=str,
                        help='file to read/write')
    parser.add_argument('-r', '--rudp', type=int, default=0,
                        help='use RUDP (1=stopwait, 2=gobackN)')
    parser.add_argument('-m', '--mcast', type=str, default='226.0.0.1',
                        help='use multicast with specified group address')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Produce verbose output')
    parser.add_argument('host', metavar='host', type=str, nargs='?',
                        help='connect to server at <host>')

    args = parser.parse_args()

    level = log.DEBUG if args.verbose else log.INFO

    f = None
    # open the file if specified
    if args.file:
        try:
            if args.host:
                mode = "rb"

            else:
                mode = "wb"

            f = open(args.file, mode)
        except Exception as e:
            print("Could not open file: {}".format(e))
            exit(1)

    if args.host:

        run_client(args, f)
    else:

        run_server(args, f)

    if args.file:
        f.close()
    exit(1)


if __name__ == "__main__":
    main()
