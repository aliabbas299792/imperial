defmodule Client do
  def start do
    receive do
      {:bind, s} -> %{s: s} |> next()
    end
  end # start

  defp next(this) do
    send(this.s, {:circle, 1.0})

    receive do
      {:result, area} -> IO.puts("Area is #{area}")
    end

    Process.sleep(1000)
    this |> next()
  end # next
end # Client
