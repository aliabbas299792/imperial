
defmodule Cluster do
  def start do
    s = Node.spawn(:'server_node@m1air', Server, :start, [])
    c = Node.spawn(:'client_node@m1air', Client, :start, [])

    send s, {:bind, c}
    send c, {:bind, s}
  end # start
end # Cluster
