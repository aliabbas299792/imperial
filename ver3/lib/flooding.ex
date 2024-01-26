# distributed algorithms, n.dulay, 4 jan 24
# lab2 -- flooding, v1

# flood message through 1-hop (fully connected) network

defmodule Flooding do
  def start do
    this = Helper.node_init()
    start(this, this.start_function)
  end

  defp bind(peers, peer_num, adjacent_nums) do
    adj_peers = Enum.map(adjacent_nums, fn idx -> Enum.at(peers, idx) end)
    send Enum.at(peers, peer_num), {:start, adj_peers}
  end

  # start

  defp start(_this, :cluster_wait) do
    :skip
  end

  # start :cluster_wait

  defp start(this, :cluster_start) do
    IO.puts("-> Flooding at #{Helper.node_string()}")

    peers =
      for p <- 0..(this.n_peers - 1),
          do: Node.spawn(:"peer#{p}_#{this.node_suffix}", Peer, :start, [p])

    flooding_unique_id = -1
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

    for [p, adj] <- network, do: bind(peers, p, adj)

    send(List.first(peers), {:hello, flooding_unique_id})
  end

  # start :cluster_start
end

# Flooding
