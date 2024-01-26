# distributed algorithms, n.dulay, 4 jan 24
# lab2 -- flooding

defmodule Peer do
  defp conditional_incr_child_cnt(this, parent_id) do
    if parent_id == this.unique_id do
      %{this | child_count: this.child_count + 1}
    else
      this
    end
  end

  defp recur_collect_recv_from_children(this, num_children_to_collect_from) do
    if num_children_to_collect_from != 0 do
      this = receive do
        {:collect_resp, parent_id, sum} ->
          if this.unique_id == parent_id do
            %{this | collected_sum: this.collected_sum + sum}
          else
            this
          end
      end
      recur_collect_recv_from_children(this, num_children_to_collect_from - 1)
    else
      this
    end
  end

  defp collect_from_children(this) do
    if not this.collection_done do
      for p <- this.peers, do: send(p, {:collect_req, self()})
      this = recur_collect_recv_from_children(this, this.child_count)
      %{this | collection_done: true}
    else
      this
    end
  end

  # a unique ID is passed in
  # then the process waits on receiving all its peers
  def start(unique_id) do
    peers =
      receive do
        {:start, peers} -> peers
      end

    # some small number
    initial_value = Helper.random(100)

    IO.puts("Initial value was: #{initial_value}")

    %{
      peers: peers,
      unique_id: unique_id,
      hello_count: 0,
      forwarded_first_hello: false,
      parent_id: "None",
      child_count: 0,
      collected_sum: initial_value,
      collection_done: false
    }
    |> next()
  end

  def next(this) do
    this =
      receive do
        {:hello, sender_id, sender_parent_id} ->
          this =
            if not this.forwarded_first_hello do
              this = %{this | parent_id: sender_id}
              for p <- this.peers, do: send(p, {:hello, this.unique_id, this.parent_id})
              %{this | forwarded_first_hello: true}
            else
              conditional_incr_child_cnt(this, sender_parent_id)
            end

          %{this | hello_count: this.hello_count + 1}

        {:collect_req, collector} ->
          this = collect_from_children(this)
          send(collector, {:collect_resp, this.parent_id, this.collected_sum})
          this
      after
        1000 ->
          IO.puts(
            "Peer <#{this.unique_id}> Parent <#{this.parent_id}> Children = <#{this.child_count}> Messages Seen = <#{this.hello_count}>"
          )

          this
      end

    this |> next()
  end
end

# Peer
