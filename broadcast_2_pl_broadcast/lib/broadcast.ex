
# distributed algorithms, n.dulay, 4 jan 24
# lab3 - broadcast algorithms

defmodule Broadcast do

def start do
  this = Helper.node_init()
  start(this, this.start_function)
end # start

defp start(_this, :cluster_wait) do :skip end

defp start(this, :cluster_start) do
  IO.puts "-> Broadcast at #{Helper.node_string()}"

  peers = for n <- 0..this.n_peers do Node.spawn(:"peer#{n}_#{this.node_suffix}", Peer, :start, [self(), n]) end
  pls = for _ <- peers do
    receive do
      {:perfect_link, pl} -> pl
    end
  end

  Process.sleep(500)
  for p <- peers do send(p, {:bind, pls}) end
  for pl <- pls do send(pl, {:broadcast, this.broadcasts, this.timeout}) end

end # start :cluster_start

end # Broadcast
