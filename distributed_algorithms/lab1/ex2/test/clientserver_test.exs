defmodule ClientserverTest do
  use ExUnit.Case
  doctest Clientserver

  test "greets the world" do
    assert Clientserver.hello() == :world
  end
end
