defmodule LossyPerfectLink do
  def start(unreliability) do
    receive do
      {:bind, beb} -> %{beb: beb, unreliability: unreliability}
    end
    |> next()
  end

  defp lossy_send(this, peer, msg) do
    if(Helper.random(100) > this.unreliability) do
      send(peer, msg)
    end
  end

  defp next(this) do
    receive do
      {:pl_send, peer, payload} ->
        lossy_send(this, peer, payload)
      outside_msg ->
        lossy_send(this, this.beb, {:pl_deliver, outside_msg})
    end
    this |> next()
  end
end
