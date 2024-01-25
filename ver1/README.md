# Version 1 of the Flooding Task
- This spawns 10 processes, and sends a `:hello` to the first one, when you run `make run cluster`
- Once `:hello` is received for the first time, each Peer sends out a `:hello` to every other Peer
- This means that the first Peer receives a total of N+1 `:hello`s (+1 due to the initial `:hello` from the `Flooding` server)
- The remaining N-1 peers receive 10 `:hello` messages each
- This is a *fully connected network* since every Peer has a link to every other Peer
- It is a *single hop* network, since each `:hello` message makes one hop, from sender to receiver
