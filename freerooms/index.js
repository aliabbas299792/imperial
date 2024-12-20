const axios = require('axios');
const express = require('express');
const { promisify } = require('util');
const exec_cmd = promisify(require('child_process').exec)

const port = 3015;
const app = express();

const MsInDay = 24 * 3600 * 1000;
const OpeningOffset = 7 * 3600 * 1000;
const locale = 'en-GB';

const days_ahead = 10;

const queries = [
  "HXLY", "SHER", "BLKT", "SAF", "BESS",
  "BEIT", "CAGB", "ACEX", "BONE", "RODH",
  "CHEM", "RSM", "ICBS", "EENG"
];

let rooms_to_dates_and_free_times = [];


function transformToUTCString(dateStr) {
  // https://en.wikipedia.org/wiki/ISO_8601#Coordinated_Universal_Time_(UTC)
  // Z used to indicate Zulu time i.e UTC time (mentioned in bit above)
  return dateStr += "Z";
}

function floorDay(date) {
  return new Date(date - (date % MsInDay));
}

function ceilDay(date) {
  return new Date(floorDay(date).getTime() + MsInDay);
}

function startOfUniDay(date) {
  return new Date(floorDay(date).getTime() + OpeningOffset);
}

function dateToLocaleTimezoneDateString(date) {
  const options = {
    timeZone: 'UTC',
    weekday: "short",
    year: "numeric",
    month: "long",
    day: "numeric",
  };

  return Intl.DateTimeFormat(locale, options).format(date);
}

function dateToLocaleTimezoneTimeString(date) {
  const options = {
    timeZone: 'UTC',
    hour: "numeric",
    minute: "numeric",
  };

  return Intl.DateTimeFormat(locale, options).format(date);
}

function containsCaseInsensitive(str, search) {
  return str.toLowerCase().indexOf(search) !== -1
}

function extractIntervalDataSorted(bookingsData) {
  // filter out information only "bookings" (checked on CELCAT these aren't room bookings)
  // and then get the dates as if they were all in UTC since it's cleaner to process them as such
  const relevantData = bookingsData
    .filter(({ eventCategory }) => !containsCaseInsensitive(eventCategory, "information"))
    .map(({ start, end, allDay }) => {
      const [startUTC, endUTC] = [start, end].map(transformToUTCString);

      const startAsDateObj = new Date(startUTC);
      // belows caps the starting time to the start of the uni day i.e 7am
      const startDate = new Date(Math.max(startAsDateObj, startOfUniDay(startAsDateObj)))
      // below "flattens" allDay events into just lasting until uni closing time i.e start of the next day
      const endDate = new Date(allDay ? (floorDay(startDate).getTime() + MsInDay) : endUTC)
      return [startDate, endDate]
    })

  relevantData.sort(([s1, _], [s2, __]) => s1 - s2);

  return relevantData;
}

function mergeConsecutiveIntervals(startEndData) {
  const merged = [];
  for (const [start, end] of startEndData) {
    if (merged.length == 0) {
      merged.push([start, end])
      continue;
    }

    const [prevStart, prevEnd] = merged[merged.length - 1];
    if (prevEnd >= start) { // flattens overlapping bookings into one
      merged.pop();
      merged.push([prevStart, new Date(Math.max(prevEnd, end))])
    } else {
      merged.push([start, end])
    }
  }
  return merged;
}

function generateIntermediateIntervals(startDate, endDate) {
  const intervals = [];
  let currDate = startDate;
  while (currDate < endDate) {
    const currDateDayStart = startOfUniDay(currDate);
    if (currDate < currDateDayStart) { // ensures it's set to open time of uni minimum
      currDate = currDateDayStart;
    }

    const endOfDay = ceilDay(currDate);
    if (endDate > endOfDay) {
      intervals.push([currDate, endOfDay])
      currDate = endOfDay;
    } else if (currDate < endDate) { // check again since we updated in the loop
      intervals.push([currDate, endDate])
      currDate = endDate;
    }
  }
  return intervals;
}

function generateAllFreeTimes(mergedData, startDate, endDate) {
  // startDate/endDate is used to ensure we get timings for the full interval we want
  const freeTimes = [];
  let currentTime = startOfUniDay(new Date(startDate));

  for (const [start, end] of mergedData) {
    freeTimes.push(...generateIntermediateIntervals(currentTime, start));
    currentTime = end;
  }

  // generates the final interval for the final day
  freeTimes.push(...generateIntermediateIntervals(currentTime, ceilDay(new Date(endDate))))

  return freeTimes;
}

function transformToPresentableData(freeTimes) {
  if (freeTimes.length == 0) {
    return [];
  }

  let currentTime = freeTimes[0][0]; // first start time
  let currentDay = floorDay(currentTime);
  let currentPresentableTimes = [];

  const presentableFreeTimes = [];
  for (const [start, end] of freeTimes) {
    const uniDayStart = startOfUniDay(start);
    if (currentTime < uniDayStart) { // new day
      presentableFreeTimes.push([dateToLocaleTimezoneDateString(currentDay), currentPresentableTimes])
      currentTime = uniDayStart;
      currentDay = floorDay(currentTime);
      currentPresentableTimes = []
    }

    currentPresentableTimes.push([start, end].map(t => dateToLocaleTimezoneTimeString(t)));
  }

  presentableFreeTimes.push([dateToLocaleTimezoneDateString(currentDay), currentPresentableTimes])

  return presentableFreeTimes;
}

function generatePresentableFreeTimes(bookingsData, startDate, endDate) {
  const relevantData = extractIntervalDataSorted(bookingsData);
  const mergedData = mergeConsecutiveIntervals(relevantData);
  const freeTimes = generateAllFreeTimes(mergedData, startDate, endDate);
  const presentableData = transformToPresentableData(freeTimes);
  return presentableData;
}

async function exec(cmd) { return (await exec_cmd(cmd)).stdout.slice(0, -1); }
async function get(url) { return (await axios.get(url)).data; }
async function post(url, data) { return (await axios.post(url, data)).data; }
async function main() {
  const rooms_to_dates_and_free_times_tmp = []
  for (const q of queries) {
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

    const presentableData = generatePresentableFreeTimes(bookings, new Date(start), new Date(end));
    rooms_to_dates_and_free_times_new.push([
      room_name,
      presentableData
    ]);
  }

  return rooms_to_dates_and_free_times_new;
}

app.use(express.static('public'))
  .get('/data', (_, res) => {
    res.send(JSON.stringify(rooms_to_dates_and_free_times))
  })

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})

main()
setInterval(main, 1000 * 60 * 60)
