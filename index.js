const axios = require('axios');
const fs = require("fs");
const { promisify } = require('util');
const exec_cmd = promisify(require('child_process').exec)

async function exec(cmd) { return (await exec_cmd(cmd)).stdout.slice(0, -1); }
async function get(url) { return (await axios.get(url)).data; }
async function post(url, data) { return (await axios.post(url, data)).data; }

let rooms_to_dates_and_free_times = [];

const queries = ["HXLY", "SHER", "BLKT", "SAF", "SKEM"]
const seconds_in_day = 60 * 60 * 24;
const day_start = 60 * 60 * 9;
const day_end = 60 * 60 * 24 - 1;
const days_ahead = 10;

function seconds_to_time(t) {
    return new Date(t * 1000).toISOString().substring(11, 16)
}

async function main() {
  const rooms_to_dates_and_free_times_tmp = []
  for(const q of queries) {
    rooms_to_dates_and_free_times_tmp.push(...(await queryTimetable(q)))
  }
  rooms_to_dates_and_free_times = rooms_to_dates_and_free_times_tmp
}

async function queryTimetable(query) {
    const get_rooms_url = `https://www.imperial.ac.uk/timetabling/calendar/Home/ReadResourceListItems?myResources=false&searchTerm=${query}&pageSize=50&pageNumber=1&resType=102`

    const start = await exec(`date "+%Y-%m-%d"`);
    const end = await exec(`date -d "+${days_ahead} days" '+%Y-%m-%d'`);

    const room_query_url = `start=${start}&end=${end}&resType=102&calView=month&federationIds%5B%5D=`;
    const room_data_post_url = "https://www.imperial.ac.uk/timetabling/calendar/Home/GetCalendarData";

    const rooms_data = await get(get_rooms_url);
    const rooms = rooms_data["results"];

    let rooms_to_dates_and_free_times_new = []

    for (const room of rooms) {
        const room_name = room["text"];
        const room_id = room["id"];

        const query_str = room_query_url + room_id;
        const bookings = await post(room_data_post_url, query_str);

        // console.log(bookings, room_data_post_url, query_str)
        fs.writeFileSync("data.txt", JSON.stringify(bookings, null, 2))

        const days_to_dates = {};
        const now_seconds = parseInt(await exec(`date -d $(date +"%D") +"%s"`));
        for (let i = 0; i < days_ahead; i++) {
            days_to_dates[now_seconds + (seconds_in_day * i)] = []
        }

        for (const booking of bookings) {
            const start = booking["start"];
            const end = booking["end"];

            if (end == null)
                continue;

            const date = await exec(`date -d "${start}" +"%D"`);
            const seconds_at_date = parseInt(await exec(`date -d "${date}" +"%s"`));
            const start_time = parseInt(await exec(`date -d "${start}" +"%s"`)) - seconds_at_date;
            const end_time = parseInt(await exec(`date -d "${end}" +"%s"`)) - seconds_at_date;

            if (!days_to_dates[seconds_at_date])
                days_to_dates[seconds_at_date] = []

            if (booking.allDay)
                days_to_dates[seconds_at_date].push([0, seconds_in_day]);

            days_to_dates[seconds_at_date].push([start_time, end_time])
        }

        let free_times_days = [];

        for (const [day, times] of Object.entries(days_to_dates)) {
            const free_times = [];
            let free_start = day_start;
            times.sort(([s1, e1], [s2, e2]) => s1 - s2)
            for (const [start, end] of times) {
                free_times.push([seconds_to_time(free_start), seconds_to_time(start)]);
                free_start = end;
            }
            if (free_start < day_end && free_start != day_start) {
                free_times.push([seconds_to_time(free_start), seconds_to_time(day_end)]);
            } else if (free_start == day_start) {
                free_times.push([seconds_to_time(day_start), seconds_to_time(day_end)]);
            }
            free_times_days.push([parseInt(day), await exec(`date -d @${day} +"%a %b %d %Y"`), free_times.filter(([s, e]) => s != e)])
        }

        if (free_times_days.length > 0)
            rooms_to_dates_and_free_times_new.push([
                room_name,
                free_times_days.sort(([t1, d1, ts1], [t2, d2, ts2]) => t1 - t2).map(([t, d, ts]) => [d, ts])
            ])
    }

    return rooms_to_dates_and_free_times_new;
}

main()
setInterval(main, 1000 * 60 * 60)

const express = require('express');
const { exit } = require('process');
const app = express()
const port = 3015

app.use(express.static('public'))
    .get('/data', (req, res) => {
        res.send(JSON.stringify(rooms_to_dates_and_free_times))
    })

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
})