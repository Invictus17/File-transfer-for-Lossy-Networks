# File-transfer-for-Lossy-Networks
A Reliable File transfer protocol built around UDP using socket programming, cumulative ACKs and SEQ numbers.

To run client:  
```$./netster.py -r 2 -f <file_name> -p <port> <server_ip>```

To run server:  
```$./netster.py -r 2 -f <file_name> -p <port> <server_ip>```
