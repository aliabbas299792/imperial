# distributed algorithms, n.dulay, 4 jan 24
# lab2 -- flooding

defmodule Peer do
  # a unique ID is passed in
  # then the process waits on receiving all its peers
  def start(unique_id) do
    peers =
      receive do
        {:start, peers} -> peers
      end

    %{peers: peers, unique_id: unique_id, hello_count: 0, forwarded_first_hello: false, parent_id: "None"} |> next()
  end

  def next(this) do
    this =
      receive do
        {:hello, sender_id} ->
          this =
            if not this.forwarded_first_hello do
              this = %{this | parent_id: sender_id}
              for p <- this.peers, do: send(p, {:hello, this.unique_id})
              %{this | forwarded_first_hello: true}
            else
              this
            end

          %{this | hello_count: this.hello_count + 1}
      after
        1000 ->
          IO.puts("Peer <#{this.unique_id}> Parent <#{this.parent_id}> Messages Seen = <#{this.hello_count}>")
          this
      end

    this |> next()
  end
end

# Peer
