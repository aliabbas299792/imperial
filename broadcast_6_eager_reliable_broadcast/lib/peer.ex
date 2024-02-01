defmodule Peer do
  def start(broadcast_pid, id, unreliability) do
    client = spawn(Client, :start, [id])
    beb = spawn(BestEffort, :start, [])
    pl = spawn(LossyPerfectLink, :start, [unreliability])
    erb = spawn(EagerReliable, :start, [])
    child_pids = [client, beb, pl, erb]

    send(broadcast_pid, {:perfect_link, pl})

    # all perfect links in network
    {ids, pls} =
      receive do
        {:bind, pls_data} ->
          ids = for {_, id} <- pls_data do id end
          pls = for {pl, _} <- pls_data do pl end
          {ids, pls}
      end

    send(pl, {:bind, beb})
    send(beb, {:bind, erb, pl, pls})
    send(erb, {:bind, client, beb})
    send(client, {:bind, ids, erb})

    if Helper.random(5) < 2 do # 1 in 5 chance of instant death
      Process.sleep(5)
      IO.puts("Exiting Peer#{id}")
      for pid <- child_pids do Process.exit(pid, :kill) end
      Process.exit(self(), :kill)
    end
  end
end
