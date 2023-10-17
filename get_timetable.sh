room="$1"

TZ=":UK" 

get_rooms_url="https://www.imperial.ac.uk/timetabling/calendar/Home/ReadResourceListItems?myResources=false&searchTerm=$room&pageSize=50&pageNumber=1&resType=102"
start=$(date '+%Y-%m-%d')
# end=$(date -d "+7 days" '+%Y-%m-%d')
end=$(date -d "+1 days" '+%Y-%m-%d')
room_query_str="start=$start&end=$end&resType=102&calView=month&federationIds%5B%5D="
room_data_post_url="https://www.imperial.ac.uk/timetabling/calendar/Home/GetCalendarData"

resp=$(curl "$get_rooms_url")
total=$(echo "$resp" | jq '.total')

for i in $(seq 0 $((total-1)))
do
	room_id=$(echo "$resp" | jq ".results[$i].id")
	room_id="${room_id%\"}"
	room_id="${room_id#\"}"
	room_name=$(echo "$resp" | jq ".results[$i].text")
	room_name="${room_name%\"}"
	room_name="${room_name#\"}"
	query_str="$room_query_str$room_id"
	room_data=$(curl -d "$query_str" -X POST $room_data_post_url)
	# echo "$room_data" | jq
	# for row in $(echo "${room_data}" | jq -r '.[]')
	# do
	#	echo "$row" | jq
	# done
	num_items=$(echo "$room_data" | jq length)
	end_date=0
	for i in $(seq 0 $((num_items-1)))
	do
		echo "$room_name"

		start_date=$(echo "$room_data" | jq ".[$i].start" | tr -d '"')
		day_diff=$(($(date -d $(date -d "$start_date" +"%D") +"%d") - $(date -d $(date -d "$end_date" +"%D") +"%d")))
		echo $day_diff
		echo $start_date
		echo $end_date
		end_date=$(echo "$room_data" | jq ".[$i].end" | tr -d '"')

		start=$(date -d "$start_date" +%s)
		end=$(date -d "$end_date" +%s)
		echo $(date -u -d @$((end - start)) +"%T")
		echo ""
	done
	end_date=0
done
