defmodule PerfectLink do
  def start do
    receive do
      {:bind, client} -> %{client: client}
    end
    |> next()
  end

  defp next(this) do
    receive do
      {:pl_send, peer, payload} ->
        send(peer, payload)
      outside_msg ->
        send(this.client, {:pl_deliver, outside_msg})
    end
    this |> next()
  end
end
