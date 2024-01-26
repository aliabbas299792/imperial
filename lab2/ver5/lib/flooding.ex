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

    network = [
      [0, [1, 6]],
      [1, [0, 2, 3]],
      [2, [1, 3, 4]],
      [3, [1, 2, 5]],
      [4, [2]],
      [5, [3]],
      [6, [0, 7]],
      [7, [6, 8, 9]],
      [8, [7, 9]],
      [9, [7, 8]]
    ]

    for [p, adj] <- network, do: bind(peers, p, adj)

    send(List.first(peers), {:hello, "None", "None"})

    # sleep 2s to let children counting be done
    Process.sleep(2000)

    send(List.first(peers), {:collect_req, self()})
    sum = receive do
      {:collect_resp, _parent_id, sum} -> sum
    end
    IO.puts("The network sum is #{sum}")

  end

  # start :cluster_start
end

# Flooding
