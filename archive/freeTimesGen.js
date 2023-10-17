const fs = require("fs");
const MsInDay = 24*3600*1000;
const OpeningOffset = 7*3600*1000;
const locale = 'en-GB';

const data = JSON.parse(fs.readFileSync("data.txt"))

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

function extractIntervalDataSorted(bookingsData) {
  const relevantData = bookingsData.map(({start, end, allDay}) => {
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
  for(const [start, end] of startEndData) {
    if(merged.length == 0) {
      merged.push([start, end])
      continue;
    }
  
    const [prevStart, prevEnd] = merged[merged.length - 1];
    if(prevEnd >= start) { // flattens overlapping bookings into one
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
  while(currDate < endDate) {
    const currDateDayStart = startOfUniDay(currDate);
    if(currDate < currDateDayStart) { // ensures it's set to open time of uni minimum
      currDate = currDateDayStart;
    }

    const endOfDay = ceilDay(currDate);
    if(endDate > endOfDay) {
      intervals.push([currDate, endOfDay])
      currDate = endOfDay;
    } else if(currDate < endDate) { // check again since we updated in the loop
      intervals.push([currDate, endDate])
      currDate = endDate;
    }
  }
  return intervals;
}

function generateAllFreeTimes(mergedData) {
  const freeTimes = [];
  let currentTime = startOfUniDay(new Date());

  for(const [start, end] of mergedData) {
    freeTimes.push(...generateIntermediateIntervals(currentTime, start));
    currentTime = end;
  }

  // generates the final interval for the final day
  freeTimes.push(...generateIntermediateIntervals(currentTime, ceilDay(currentTime)))

  return freeTimes;
}

function transformToPresentableData(freeTimes) {
  if(freeTimes.length == 0) {
    return [];
  }

  let currentTime = freeTimes[0][0]; // first start time
  let currentDay = floorDay(currentTime);
  let currentPresentableTimes = [];

  const presentableFreeTimes = [];
  for(const [start, end] of freeTimes) {
    const uniDayStart = startOfUniDay(start);
    if(currentTime < uniDayStart) { // new day
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

function generatePresentableFreeTimes(bookingsData) {
  const relevantData = extractIntervalDataSorted(bookingsData);
  const mergedData = mergeConsecutiveIntervals(relevantData);
  const freeTimes = generateAllFreeTimes(mergedData);
  const presentableData = transformToPresentableData(freeTimes);
  return presentableData;
}

const presentableData = generatePresentableFreeTimes(data);

console.dir(presentableData, { depth: null })

// todo, now change this all so that it is in the correct timezone