
# distributed algorithms, n.dulay, 4 jan 24
# simple client-server, v1

defmodule Server do

def start do
  IO.puts "-> Server at #{Helper.node_string()}"
  %{} |> next()
end # start

defp heron_area(a, b, c) do
  s = (a+b+c)/2
  Helper.sqrt(s*(s-a)*(s-b)*(s-c))
end

defp next(this) do
  # instead of taking a single client id, we take
  # the client id when receiving the message, and respond to
  # that client using the provided id

  # deals with 3 different requests
  receive do
    { :circle, radius, client_id } ->
      send client_id, { :result, 3.14159 * radius * radius }
    { :square, side, client_id } ->
      send client_id, { :result, side * side }
    { :triangle, a, b, c, client_id } ->
      send client_id, { :result, heron_area(a, b, c) }
  end # receive
  this |> next()
end # next

end # Server
