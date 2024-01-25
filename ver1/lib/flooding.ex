# distributed algorithms, n.dulay, 4 jan 24
# lab2 -- flooding, v1

# flood message through 1-hop (fully connected) network

defmodule Flooding do
  def start do
    this = Helper.node_init()
    start(this, this.start_function)
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

    for peer <- peers, do: send(peer, {:start, peers})

    send List.first(peers), :hello
  end

  # start :cluster_start
end

# Flooding
