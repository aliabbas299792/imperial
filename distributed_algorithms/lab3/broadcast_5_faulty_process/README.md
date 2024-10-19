# Faulty Process
This time all that was changed was that peer now terminates sometimes randomly after 5ms.
Since the BEB module is fail-silent, a faulty link is indistinguishable from its fail-silent behaviour, so the output looks basically the same (I've added exit messages to know that it is exiting though):
```
Exiting Peer5
Exiting Peer3
Peer 0: {1000 639} {1000 645} {1000 644} {1000 638} {1000 636} {1000 625}
Peer 1: {1000 620} {1000 630} {1000 647} {1000 624} {1000 627} {1000 655}
Peer 2: {1000 629} {1000 663} {1000 642} {1000 638} {1000 646} {1000 641}
Peer 4: {1000 648} {1000 635} {1000 614} {1000 636} {1000 641} {1000 656}
```