
# distributed algorithms, n.dulay, 4 jan 24
# simple client-server, v1

defmodule Server do
 
def start do 
  IO.puts "-> Server at #{Helper.node_string()}"
  receive do
    { :bind, client } -> %{client: client} |> next() 
  end # receive
end # start
 
defp next(this) do
  receive do
    { :circle, radius } -> 
      send this.client, { :result, 3.14159 * radius * radius }
    { :square, side } -> 
      send this.client, { :result, side * side }
  end # receive
  this |> next()
end # next

end # Server

