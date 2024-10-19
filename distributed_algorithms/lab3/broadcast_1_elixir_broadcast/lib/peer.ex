defmodule Peer do
  def start(id) do
    peers =
      receive do
        {:init, peers} -> peers
      end

    # broadcasted by us and delivered to us
    %{id: id, peers: peers, broadcasted: %{}, delivered: %{}, max_broadcasts: nil} |> next()
  end

  defp send_broadcast(this) do
    Enum.reduce(this.peers, this, fn peer, this ->
      if Map.get(this.broadcasted, peer, 0) != this.max_broadcasts do
        send(self(), {:process_buffered_send, peer})

        %{
          this
          | broadcasted: Map.update(this.broadcasted, peer, 1, fn old_val -> old_val + 1 end)
        }
      else
        this
      end
    end)
  end

  defp next(this) do
    receive do
      {:broadcast, max_broadcasts, timeout} ->
        # expects to receive a single :broadcast message
        this = %{this | max_broadcasts: max_broadcasts}

        Process.send_after(self(), :timeout, timeout)

        # initial broadcast
        this |> send_broadcast() |> next()

      {:propagate_broadcast, sender} ->
        # received 1 message
        this = %{
          this
          | delivered: Map.update(this.delivered, sender, 1, fn old_val -> old_val + 1 end)
        }

        # set out plan to send out messages to all peers
        this |> send_broadcast() |> next()

      {:process_buffered_send, peer} ->
        # for each "plan" (i.e buffered send) send out a broadcast
        send(peer, {:propagate_broadcast, self()})
        this |> next()

      :timeout ->
        IO.puts(
          "Peer #{this.id}: #{Enum.join(for p <- this.peers do
            "{#{this.broadcasted[p]} #{this.delivered[p]}}"
          end,
          " ")}"
        )
    end
  end
end
