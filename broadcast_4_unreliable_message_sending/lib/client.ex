defmodule Client do
  def start(id) do
    remote_data =
      receive do
        {:bind, peer_ids, beb} -> %{peer_ids: peer_ids, beb: beb}
      end

    this =
      Map.merge(
        %{id: id, broadcasted: %{}, delivered: %{}, max_broadcasts: nil},
        remote_data
      )

    this =
      receive do
        # expects to receive a single :broadcast message
        {:beb_deliver, {:broadcast, max_broadcasts, timeout}} ->
          Process.send_after(self(), :timeout, timeout)
          %{this | max_broadcasts: max_broadcasts}
      end

    # initial broadcast
    this |> beb_broadcast() |> next()
  end

  defp beb_broadcast(this) do
    {new_this, allow_broadcasts} =
      Enum.reduce(this.peer_ids, {this, true}, fn peer_id, {this, allow_broadcasts} ->
        {%{
           this
           | broadcasted: Map.update(this.broadcasted, peer_id, 1, fn old_val -> old_val + 1 end)
         }, allow_broadcasts and Map.get(this.broadcasted, peer_id, 0) < this.max_broadcasts}
      end)

    if allow_broadcasts do
      send(new_this.beb, {:beb_broadcast, {:propagate_broadcast, new_this.id}})
      new_this
    else
      this
    end
  end

  defp next(this) do
    receive do
      {:beb_deliver, {:propagate_broadcast, sender_id}} ->
        # received 1 message
        this = %{
          this
          | delivered: Map.update(this.delivered, sender_id, 1, fn old_val -> old_val + 1 end)
        }

        # set out plan to send out messages to all peers
        this |> beb_broadcast() |> next()

      :timeout ->
        IO.puts(
          "Peer #{this.id}: #{Enum.join(for p <- this.peer_ids do
            "{#{Map.get(this.broadcasted, p, 0)} #{Map.get(this.delivered, p, 0)}}"
          end,
          " ")}"
        )
    end
  end
end
