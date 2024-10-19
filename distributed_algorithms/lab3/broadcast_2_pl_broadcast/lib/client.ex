defmodule Client do
  def start(id) do
    {pl, peers} =
      receive do
        {:bind, pl, peers} -> {pl, peers}
      end

    %{
      pl: pl,
      peers: peers,
      id: id,
      buffered_broadcasts: [],
      broadcasted: %{},
      delivered: %{},
      max_broadcasts: nil
    }
    |> next()
  end

  defp buffer_broadcast(this) do
    Enum.reduce(this.peers, this, fn peer, this ->
      if Map.get(this.broadcasted, peer, 0) != this.max_broadcasts do
        %{
          this
          | broadcasted: Map.update(this.broadcasted, peer, 1, fn old_val -> old_val + 1 end),
            buffered_broadcasts: [peer | this.buffered_broadcasts]
        }
      else
        this
      end
    end)
  end

  defp pl_send(this, peer, payload) do
    send(this.pl, {:pl_send, peer, payload})
  end

  defp process_one_buffered_broadcast(this) do
    if this.buffered_broadcasts != [] do
      [peer | tail] = this.buffered_broadcasts
      pl_send(this, peer, {:propagate_broadcast, this.pl})
      %{this | buffered_broadcasts: tail}
    else
      this
    end
  end

  defp next(this) do
    receive do
      {:pl_deliver, {:broadcast, max_broadcasts, timeout}} ->
        # expects to receive a single :broadcast message
        this = %{this | max_broadcasts: max_broadcasts}

        Process.send_after(self(), :timeout, timeout)

        # initial broadcast
        this |> buffer_broadcast() |> next()

      {:pl_deliver, {:propagate_broadcast, sender}} ->
        # received 1 message
        this = %{
          this
          | delivered: Map.update(this.delivered, sender, 1, fn old_val -> old_val + 1 end)
        }

        # set out plan to send out messages to all peers
        this |> buffer_broadcast() |> next()

      :timeout ->
        IO.puts(
          "Peer #{this.id}: #{Enum.join(for p <- this.peers do
            "{#{this.broadcasted[p]} #{this.delivered[p]}}"
          end,
          " ")}"
        )
    after
      0 -> this |> process_one_buffered_broadcast() |> next()
    end
  end
end
