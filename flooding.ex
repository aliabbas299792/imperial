# distributed algorithms, n.dulay, 4 jan 24
# lab2 -- flooding, v1

# flood message through 1-hop (fully connected) network

defmodule Flooding do

def start do 
  this = Helper.node_init()
  start(this, this.start_function) 
end # start

defp start(_this, :cluster_wait) do
  :skip
end # start :cluster_wait

defp start(this, :cluster_start) do
  IO.puts "-> Flooding at #{Helper.node_string()}"

  # **** ADD YOUR CODE HERE ****

end # start :cluster_start

end # Flooding

