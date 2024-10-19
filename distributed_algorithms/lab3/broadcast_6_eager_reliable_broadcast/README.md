# ERB Broadcasting
For the longest time I was stuck at ERB not propagating messages to the client, then I realised I didn't put any unique information in the message so it was getting filtered when I was checking for duplicate sends in there.

With 3s timeout, 1000 messages and 0 unreliability, even with a node crashing you see that all correct processes receive every single message:
```
Exiting Peer1
Peer 2: {1000 1000} {1000 863} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Peer 0: {1000 1000} {1000 863} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Peer 3: {1000 1000} {1000 863} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Peer 5: {1000 1000} {1000 863} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Peer 4: {1000 1000} {1000 863} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Final ERB delivered set size: 5869
Final ERB delivered set size: 5869
Final ERB delivered set size: 5869
Final ERB delivered set size: 5869
Final ERB delivered set size: 5869
```
You can see as well that the peers are likely in consensus on the amount of messages received due to having exactly the same deliver set sizes in the end.

By changing the unreliability to 20, more messages are lost, but a lot more make it through than did in i.e task 5:
```
Exiting Peer5
Exiting Peer1
Peer 2: {1000 966} {1000 850} {1000 966} {1000 968} {1000 959} {1000 248}
Peer 3: {1000 959} {1000 846} {1000 965} {1000 971} {1000 964} {1000 247}
Peer 4: {1000 965} {1000 846} {1000 962} {1000 963} {1000 965} {1000 250}
Peer 0: {1000 956} {1000 844} {1000 959} {1000 966} {1000 964} {1000 248}
Final ERB delivered set size: 4956
Final ERB delivered set size: 4961
Final ERB delivered set size: 4941
Final ERB delivered set size: 4955
```
But we note that due to the lossy nature of the link, messages may not always be delivered, and so even with a reliable broadcast, the delivered set sizes are not exactly the same (they are close though), and indeed this is also why the correct processes have not all received 1000 messages.

Interesting to note there too is that we can see that peer 5 probably only managed to receive a few messages before exiting, and peer 1 nearly got all of its ones before exiting, as reflected in their received/delivered message count.