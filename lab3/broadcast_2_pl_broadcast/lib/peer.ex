defmodule Peer do
  def start(broadcast_pid, id) do
    client = spawn(Client, :start, [id])
    pl = spawn(PerfectLink, :start, [])

    send(broadcast_pid, {:perfect_link, pl})

    # all perfect links in network
    pls =
      receive do
        {:bind, pls} -> pls
      end

    send(pl, {:bind, client})
    send(client, {:bind, pl, pls})
  end
end
