
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

  peer_data = for n <- 0..this.n_peers do
    node = Node.spawn(:"peer#{n}_#{this.node_suffix}", Peer, :start, [self(), n, this.unreliability])
    {node, n}
  end
  pls_data = for {_, id} <- peer_data do
    receive do
      {:perfect_link, pl} -> {pl, id}
    end
  end

  Process.sleep(500)
  for {peer_node, _} <- peer_data do send(peer_node, {:bind, pls_data}) end
  for {pl, n} <- pls_data do send(pl, {:rb_data, n, {:broadcast, this.broadcasts, this.timeout}}) end

end # start :cluster_start

end # Broadcast
