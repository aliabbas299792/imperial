# distributed algorithms, n.dulay, 4 jan 24
# simple client-server, v1

defmodule ClientServer do
  def start do
    this = Helper.node_init()
    start(this, this.start_function)
  end

  # start

  defp start(_this, :cluster_wait) do
    :skip
  end

  # start :cluster_wait

  defp start(this, :single_start) do
    IO.puts("-> ClientServer at #{Helper.node_string()}")
    server = Node.spawn(:"clientserver_#{this.node_suffix}", Server, :start, [])

    for _ <- 1..this.num_clients,
        do: Node.spawn(:"clientserver_#{this.node_suffix}", Client, :start, [server])
  end

  # start :single_start

  defp start(this, :cluster_start) do
    IO.puts("-> ClientServer at #{Helper.node_string()}")
    server = Node.spawn(:"server_#{this.node_suffix}", Server, :start, [])
    # give the server some time to start up
    Process.sleep(500)

    for n <- 1..this.num_clients,
        do: Node.spawn(:"client#{n}_#{this.node_suffix}", Client, :start, [server])
  end

  # start :cluster_start

  # running "make ps" while running "make single" or "make cluster" we can see
end

# ClientServer
