
# distributed algorithms, n.dulay, 4 jan 24
# simple client-server, v1

defmodule Client do

def start do
  IO.puts "-> Client at #{Helper.node_string()}"
  receive do
    { :bind, server } -> %{server: server} |> next()
  end # receive
end # start

defp next(this) do
  send this.server, { :circle, 1.0 }
  receive do { :result, area } -> IO.puts "Area is #{area}" end
  Process.sleep(1000)
  this |> next()
end # next

end # Client

