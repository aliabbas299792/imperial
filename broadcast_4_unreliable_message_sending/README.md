# BEB Broadcast
This version has each peer made up like this:
```
Client -> BEB -> PL ----network---- other clients
```
And the actual broadcasting interleaving is now handled in the BEB module.

Once more I see that the average performance has gotten worse (10 million messages, 3 seconds):
```
Peer 1: {89584 12216} {89584 14135} {89584 15647} {89584 15860} {89584 15861} {89584 15864}
Peer 0: {95552 16315} {95552 15861} {95552 15762} {95552 15888} {95552 15861} {95552 15864}
Peer 5: {25157 2856} {25157 3015} {25157 1467} {25157 6229} {25157 5243} {25157 6346}
Peer 4: {61914 10397} {61914 11220} {61914 9478} {61914 10383} {61914 10367} {61914 10068}
Peer 3: {97086 12562} {97086 15860} {97086 16079} {97086 20861} {97086 15860} {97086 15863}
Peer 2: {67355 2271} {67355 2280} {67355 55948} {67355 2293} {67355 2265} {67355 2297}
```