defmodule EagerReliable do
  def start do
    receive do
      {:bind, client, beb} -> %{client: client, beb: beb, delivered: MapSet.new()} |> next()
    end
  end

  defp generate_unique_id() do
    # used purely for deduplication on the ERB level
    to_string(:erlang.ref_to_list(:erlang.make_ref()))
  end

  defp next(this) do
    receive do
      {:rb_broadcast, msg} ->
        send(this.beb, {:beb_broadcast, {:rb_data, generate_unique_id(), msg}})
        this |> next()

      {:beb_deliver, {:rb_data, _unique_info, msg} = data} ->
        if data in this.delivered do
          this |> next()
        else
          send(this.client, {:rb_deliver, msg})
          send(this.beb, {:beb_broadcast, data})
          %{this | delivered: MapSet.put(this.delivered, data)} |> next()
        end
    after
      5_000 -> IO.puts("Final ERB delivered set size: #{MapSet.size(this.delivered)}")
    end
  end
end
