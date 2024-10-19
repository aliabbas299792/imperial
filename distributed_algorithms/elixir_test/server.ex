defmodule Server do
  def start do
    receive do
      {:bind, c} -> %{c: c} |> next()
    end
  end # start

  defp next(this) do
    receive do
      {:circle, r} -> send this.c, {:result, 3.14159 * r * r}
      {:square, side} -> send this.c, {:result, side * side}
    end

    this |> next()
  end # next
end # Server
