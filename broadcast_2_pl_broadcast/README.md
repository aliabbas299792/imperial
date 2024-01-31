# PL Broadcast
This version has a perfect link and a client making up each Peer.
- I also changed the interleaving design to use an internal list to track which peers I need to send to, and I use a non blocking `receive` block to take one off on each loop (by setting the timeout time to 0)

I set the max timeout to be 3s and set there to be 1,000,000 broadcasts:
```
Peer 2: {111509 20828} {111509 21343} {111509 17513} {111509 17196} {111509 17422} {111509 17206}
Peer 4: {49535 7324} {49535 7744} {49535 8288} {49535 7135} {49535 13018} {49535 6025}
Peer 3: {26488 3551} {26488 5112} {26488 7148} {26488 7973} {26488 1481} {26488 1222}
Peer 1: {23518 1311} {23518 15434} {23518 1473} {23518 1334} {23518 2631} {23518 1334}
Peer 5: {44567 7139} {44567 9406} {44567 7338} {44567 5931} {44567 5065} {44567 9687}
Peer 0: {134118 85724} {134118 11668} {134118 10826} {134118 8802} {134118 8864} {134118 8233}
```
As you can see, despite making the processing more efficient, introduction of the PL abstraction did pretty substantially slow down performance vs the same case in task 1.