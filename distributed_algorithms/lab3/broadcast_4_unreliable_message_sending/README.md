# Lossy PL Link Broadcast
This time the architecture of peers was basically the same as last time, but with a lossy PL:
```
Client -> BEB -> Lossy PL
```
I ran the broadcasting with an `unreliability` parameter of `20` (i.e about 20% of messages are dropped), and got this:
```
Peer 2: {1000 638} {1000 0} {1000 626} {1000 0} {1000 0} {1000 640}
Peer 0: {1000 633} {1000 0} {1000 669} {1000 0} {1000 0} {1000 653}
Peer 5: {1000 603} {1000 0} {1000 652} {1000 0} {1000 0} {1000 658}
```
Interestingly peers 1, 3 and 4 never even spawn, this is because the initial `:broadcast` message got dropped.
Also we see that a lot fewer messages are actually received, this is due to the same dropout.