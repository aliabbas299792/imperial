defmodule Client do
  def start(id) do
    remote_data =
      receive do
        {:bind, peer_ids, erb} -> %{peer_ids: peer_ids, erb: erb}
      end

    this =
      Map.merge(
        %{id: id, broadcasted: %{}, delivered: %{}, max_broadcasts: nil},
        remote_data
      )

    this =
      receive do
        # expects to receive a single :broadcast message
        {:rb_deliver, {:broadcast, max_broadcasts, timeout}} ->
          Process.send_after(self(), :timeout, timeout)
          %{this | max_broadcasts: max_broadcasts}
      end

    # initial broadcast
    this |> erb_broadcast() |> next()
  end

  defp erb_broadcast(this) do
    {new_this, allow_broadcasts} =
      Enum.reduce(this.peer_ids, {this, true}, fn peer_id, {this, allow_broadcasts} ->
        {%{
           this
           | broadcasted: Map.update(this.broadcasted, peer_id, 1, fn old_val -> old_val + 1 end)
         }, allow_broadcasts and Map.get(this.broadcasted, peer_id, 0) < this.max_broadcasts}
      end)

    if allow_broadcasts do
      send(new_this.erb, {:rb_broadcast, {:propagate_broadcast, new_this.id}})
      new_this
    else
      this
    end
  end

  defp next(this) do
    receive do
      {:rb_deliver, {:propagate_broadcast, sender_id}} ->
        # received 1 message
        this = %{
          this
          | delivered: Map.update(this.delivered, sender_id, 1, fn old_val -> old_val + 1 end)
        }

        # set out plan to send out messages to all peers
        this |> erb_broadcast() |> next()

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
