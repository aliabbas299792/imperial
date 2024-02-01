defmodule Peer do
  def start(broadcast_pid, id, unreliability) do
    client = spawn(Client, :start, [id])
    beb = spawn(BestEffort, :start, [])
    pl = spawn(LossyPerfectLink, :start, [unreliability])
    child_pids = [client, beb, pl]

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
    send(beb, {:bind, client, pl, pls})
    send(client, {:bind, ids, beb})

    if Helper.random(5) < 2 do # 1 in 5 chance of instant death
      Process.sleep(5)
      IO.puts("Exiting Peer#{id}")
      for pid <- child_pids do Process.exit(pid, :kill) end
      Process.exit(self(), :kill)
    end
  end
end


# [
#   {#PID<20132.140.0>, 0},
#   {#PID<0.140.0>, 1},
#   {#PID<20184.140.0>, 2},
#   {#PID<20185.140.0>, 3},
#   {#PID<20187.140.0>, 4},
#   {#PID<20186.140.0>, 5}
# ]
