
# distributed algorithms, n.dulay, 4 jan 24
# simple client-server, v1

defmodule Client do

def start(server) do
  IO.puts "-> Client at #{Helper.node_string()}"
  %{server: server} |> next()
end # start

defp next(this) do
  # send 1 of 3 cases randomly
  rand = Helper.random(3)
  shape = case rand do
     1 ->
      send this.server, { :triangle, 3.0, 4.0, 5.0, self() }
      "triangle"
     2 ->
      send this.server, { :square, 1.0, self() }
      "square"
     3 ->
      send this.server, { :circle, 1.0, self() }
      "circle"
  end

  receive do { :result, area } -> IO.puts "Area of shape #{shape} is #{area} for pid #{inspect(self())}" end
  Process.sleep(Helper.random(2000)+1000) # randomly sleep between 1 and 3 seconds
  this |> next()
end # next

end # Client
