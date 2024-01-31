
# distributed algorithms, n.dulay, 4 jan 24 
# lab3 - broadcast algorithms

PEERS    = 5
START    = Broadcast.start
MAX_TIME = 15000

HOST	:= 127.0.0.1

# --------------------------------------------------------------------

TIME    := $(shell date +%H:%M:%S)
SECS    := $(shell date +%S)
COOKIE  := $(shell echo $$PPID)

NODE_SUFFIX := ${SECS}_${LOGNAME}@${HOST}
 
ERLANG := "-kernel prevent_overlapping_partitions false" 
ELIXIR := elixir --no-halt --cookie ${COOKIE} --erl ${ERLANG} --name
MIX    := -S mix run -e ${START} ${MAX_TIME} ${NODE_SUFFIX} ${PEERS}

# --------------------------------------------------------------------

run cluster: compile
	@for k in `seq 0 ${PEERS}`; do \
		(${ELIXIR} peer$${k}_${NODE_SUFFIX} ${MIX} cluster_wait &) ; \
	done 

	@sleep 3
	@ ${ELIXIR} broadcast_${NODE_SUFFIX} ${MIX} cluster_start

compile:
	mix compile

clean:
	mix clean
	@rm -f erl_crash.dump

ps:
	@echo ------------------------------------------------------------
	epmd -names

