defmodule BestEffort do
  def start do
    receive do
      {:bind, erb, pl, peers} -> %{erb: erb, pl: pl, peers: peers}
    end |> next()
  end

  defp next(this) do
    receive do
      {:beb_broadcast, payload} ->
        for p <- this.peers do send(this.pl, {:pl_send, p, payload}) end
      {:pl_deliver, payload} ->
        send(this.erb, {:beb_deliver, payload})
    end
    this |> next()
  end
end
