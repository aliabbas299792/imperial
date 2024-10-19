defmodule PerfectLink do
  def start do
    receive do
      {:bind, beb} -> %{beb: beb}
    end
    |> next()
  end

  defp next(this) do
    receive do
      {:pl_send, peer, payload} ->
        send(peer, payload)
      outside_msg ->
        send(this.beb, {:pl_deliver, outside_msg})
    end
    this |> next()
  end
end
