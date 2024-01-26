# Version 5 of the Flooding Task
The idea here is that when a Peer receives a collection request, it should wait for all its children to return a value before returning a value.
Sample output:
```
Initial value was: 46
Initial value was: 8
Initial value was: 97
Initial value was: 5
Initial value was: 38
Initial value was: 14
Initial value was: 23
Initial value was: 89
Initial value was: 24
Initial value was: 14
Peer <0> Parent <None> Children = <2> Messages Seen = <3>
Peer <6> Parent <0> Children = <1> Messages Seen = <2>
Peer <1> Parent <0> Children = <2> Messages Seen = <3>
Peer <2> Parent <1> Children = <1> Messages Seen = <3>
Peer <5> Parent <3> Children = <0> Messages Seen = <1>
Peer <4> Parent <2> Children = <0> Messages Seen = <1>
Peer <3> Parent <1> Children = <1> Messages Seen = <3>
Peer <7> Parent <6> Children = <2> Messages Seen = <3>
Peer <9> Parent <7> Children = <0> Messages Seen = <2>
Peer <8> Parent <7> Children = <0> Messages Seen = <2>
The network sum is 358
```
The `Initial value was: ...` lines are printed by each peer, with the value they were randomly initialised to, and at the bottom you can see the network sum (which correctly sums all of those values).

I had to have a 2s sleep between the `:hello` messages and the summation here because otherwise the number of children wouldn't be counted correctly so the summations would be less than what you'd want.
