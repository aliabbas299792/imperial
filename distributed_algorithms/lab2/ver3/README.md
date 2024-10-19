# Version 3 of the Flooding Task
This task demonstrates how you can use the flooding algorithm to build a spanning tree of the network by recording the first Peer to send you a `:hello` message as your parent.
This is not necessarily be the most optimal spanning tree for some network configuration (in terms of how shallow it is - it could possibly be shallower).
Sample output:
```
Peer <0> Parent <-1> Messages Seen = <3>
Peer <6> Parent <0> Messages Seen = <2>
Peer <1> Parent <0> Messages Seen = <3>
Peer <7> Parent <6> Messages Seen = <3>
Peer <2> Parent <1> Messages Seen = <3>
Peer <4> Parent <2> Messages Seen = <1>
Peer <5> Parent <3> Messages Seen = <1>
Peer <3> Parent <1> Messages Seen = <3>
Peer <8> Parent <7> Messages Seen = <2>
Peer <9> Parent <7> Messages Seen = <2>
```
### Pipeline Network
By altering the network setup, here is how it'd look if there were a pipeline of Peers instead:
```
Peer <0> Parent <-1> Messages Seen = <1>
Peer <1> Parent <0> Messages Seen = <1>
Peer <2> Parent <1> Messages Seen = <1>
Peer <3> Parent <2> Messages Seen = <1>
Peer <4> Parent <3> Messages Seen = <1>
Peer <5> Parent <4> Messages Seen = <1>
Peer <6> Parent <5> Messages Seen = <1>
Peer <7> Parent <6> Messages Seen = <1>
Peer <8> Parent <7> Messages Seen = <2>
Peer <9> Parent <8> Messages Seen = <1>
```
So the spanning tree looks like this (in terms of parent->child connections):
```
(-1) -> 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9
```
This was achieved by setting the `network` variable (i.e the network configuration) as such:
```elixir
network = [
  [0, [1]],
  [1, [2]],
  [2, [3]],
  [3, [4]],
  [4, [5]],
  [5, [6]],
  [6, [7]],
  [7, [8]],
  [8, [9]],
  [9, [8]]
]
```