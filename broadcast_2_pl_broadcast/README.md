# Elixir Broadcast
The setup appears to be a central `Broadcast` module, which should then spawn a number of `Peer` modules, so I'll start off by making a `Peer` module.
- The peers should receive a broadcast, and increment a counter, and increment another counter if they make a broadcast
- I achieved the interleaving effect by separating out actually broadcasting messages to another receive response, I send a message to itself telling the Peer to send a broadcast to another peer

The interleaving mechanics are not ideal, I could instead maybe use a non blocking version of `receive` and maintain a list of peers to broadcast to which would improve throughput.

1. With 1000 messages and 3 seconds, all messages are successfully sent an received:
```
Peer 2: {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Peer 0: {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Peer 4: {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Peer 3: {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Peer 1: {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
Peer 5: {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000} {1000 1000}
```
2. With 10,000,000 messages and 3 seconds:
```
Peer 1: {79091 3337} {79091 62381} {79091 3336} {79091 3357} {79091 3335} {79091 3344}
Peer 3: {121332 13325} {121332 54700} {121332 13206} {121332 13398} {121332 13326} {121332 13376}
Peer 2: {121201 13325} {121201 54569} {121201 13206} {121201 13398} {121201 13326} {121201 13376}
Peer 0: {121024 13326} {121024 54387} {121024 13207} {121024 13399} {121024 13327} {121024 13377}
Peer 4: {121189 13325} {121189 54557} {121189 13206} {121189 13398} {121189 13326} {121189 13376}
Peer 5: {119726 13325} {119726 53094} {119726 13206} {119726 13398} {119726 13326} {119726 13376}
```
Not many are sent and received out of the total, with something like 250,000 sent and only about 40,000 received. This is likely due to my design of the server with each broadcast resulting in N further messages being sent to the same Peer to indicate that a future broadcast should be made. Interestingly if we factor in the amount of received messages, and then the amount which had to have been received to get the number of broadcasts we see (i.e 40,000 received, for each of those 5 more sent off), then you see that the amount of messages sent and received in total is roughly the same on average, in the ballpark of 250,000.
3. Another case I tested was 1,000,000 messages in 120 seconds:
```
Peer 5: {1000000 382211} {1000000 353074} {1000000 363735} {1000000 581987} {1000000 336721} {1000000 990521}
Peer 4: {1000000 407516} {1000000 378392} {1000000 407430} {1000000 682387} {1000000 353544} {1000000 967650}
Peer 3: {1000000 407516} {1000000 378392} {1000000 407430} {1000000 682387} {1000000 353544} {1000000 967631}
Peer 0: {1000000 407516} {1000000 378392} {1000000 407430} {1000000 682387} {1000000 353544} {1000000 967651}
Peer 2: {1000000 407516} {1000000 378392} {1000000 407430} {1000000 682387} {1000000 353544} {1000000 967651}
Peer 1: {1000000 407516} {1000000 378392} {1000000 407430} {1000000 682387} {1000000 353544} {1000000 967651}
```
As you can see, it seems that the deliver queue for all nodes seem to struggle to catch up to the amount of messages each has broadcast. This is again due to how a single broadcast received spawns a further 5 sends.

This is further evidenced by the fact that all nodes have delivered more than 166,667 messages which means that they all have met the minimum threshold of messages received to be able to tentatively broadcast that many.

Note that just because the broadcasted column shows 1,000,000, it doesn't mean all 1,000,000 have been sent to the other node just yet, just that they've been put into the nodes receive message queue to process as a job which then will actually send out the messages, and, like case 2. above, this is why there is such a large gap.

We can also see that how the nodes deliver is quite unfair as well, it seems like broadcasts to/from the 5th node are being processed much faster than for other nodes.