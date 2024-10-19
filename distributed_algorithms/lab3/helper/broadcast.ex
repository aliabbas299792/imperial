
# distributed algorithms, n.dulay, 4 jan 24
# lab3 - broadcast algorithms

defmodule Broadcast do

def start do 
  this = Helper.node_init()
  start(this, this.start_function) 
end # start

defp start(_this, :cluster_wait) do :skip end

defp start(this, :cluster_start) do
  IO.puts "-> Broadcast at #{Helper.node_string()}"

  # **** ADD YOUR CODE HERE ****

end # start :cluster_start

end # Broadcast

