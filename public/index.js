const data_div = document.querySelector("#data");
const free_now_div = document.querySelector("#free_now");
const seconds_in_day = 3600 * 24;
const timeView = document.getElementById("viewTime");
const dateView = document.getElementById("viewDate");
const searchBtn = document.getElementById("searchTimes");
const resetTimeBtn = document.getElementById("resetTime");
let data_obj = [];

function getSearchDateTime() {
  const urlData = new URLSearchParams(window.location.search);
  const date = urlData.get("date");
  const time = urlData.get("time");
  const d = new Date();
  return [date ? getDateStr(new Date(date)) : getDateStr(d), time ? time : timeStr(d)];
}

function getDateStr(d) {
  const day = d.getDate();
  const month = d.getMonth() + 1;
  const year = d.getFullYear();
  return `${year}-${month}-${day}`;
}

function numStrPad0(num, pad) {
  return `${num}`.padStart(pad, '0')
}

function timeStr(d) {
  return `${numStrPad0(d.getHours(), 2)}:${numStrPad0(d.getMinutes(), 2)}`;
}

function getSearchString() {
  const date = dateView.value;
  const time = timeView.value;
  return `?date=${date}&time=${time}`;
}

searchBtn.onclick = () => {
  window.location.href = window.location.origin + getSearchString();
}

resetTimeBtn.onclick = () => {
  dateView.value = getDateStr(new Date());
  timeView.value = timeStr(new Date());
  searchBtn.click();
}

window.onload = () => {
  const [date, time] = getSearchDateTime();
  timeView.value = time;
  dateView.value = date;
}

function to_seconds(t) {
  const [h, m] = t.split(":");
  return h * 3600 + m * 60;
}

function time_in_range([start, end], time, excludeEnd) {
  start = to_seconds(start);
  end = to_seconds(end);
  time = to_seconds(time);

  if (start <= time && end == 0) { // special case where end is the next day
    return excludeEnd ? time != end : true;
  }

  if (excludeEnd) {
    return start <= time && time < end;
  }

  return start <= time && time <= end;
}

fetch("/data").then(res => res.json()).then(r => {
  for (const room of r) {
    const [name, days] = room;
    let html_str = `<div class='room-block'><h2 class='room'>${name}</h2>`;
    for (const [date, times] of days) {
      html_str += `<div class='date-block'><h4 class='date'>${date}</h4>`;
      html_str += `Free: ` + times.map(t => t.map(time => `<span class='time'>${time}</span>`).join(" to ")).join(", ")
      html_str += `</div>`;
    }
    html_str += "</div>";
    data_div.innerHTML += html_str;
  }

  data_obj = r
})
  .then(_ => {
    const free_now = find_a_room_now();
    for (const [room, [start, end], then] of free_now) {
      free_now_div.innerHTML += `<tr><td>${room}</td><!--<td><span class='time'>${start}</span></td>--><td><span class='time'>${end}</span></td><td><span class='thenTime'>${then}</span></td>`;
    }
  })


let globalCounter = 0;

function changeShownHidden(id, btnId) {
  const el = document.querySelector(`#${id}`);
  const btn = document.querySelector(`#${btnId}`);
  const notShown = el.style.display != 'block';

  if (notShown) {
    el.style.display = 'block';
    btn.innerText = "Hide places to go after";
  } else {
    el.style.display = 'none';
    btn.innerText = "Show places to go after";
  }
}

function find_a_room_now() {
  const today = (new Date(dateView.value)).toString().slice(0, 15);
  const now = timeView.value;
  const free_now = [];

  const until = new Set();
  const todayBookings = [];

  for ([room, days] of data_obj) {
    for (roomData of days) {
      const [day, times] = roomData;
      if (new Date(day).getTime() == new Date(today).getTime()) {
        todayBookings.push([room, times])
        for (const [start, end] of times) {
          // special case where the end time is the end of the day, i.e 0s of the next day
          if (to_seconds(end) > to_seconds(now) || to_seconds(end) == 0) {
            until.add(end)
          }
        }
      }
    }
  }

  console.log(until)

  const untilMap = {};
  for (const [room, times] of todayBookings) {
    for (const u of until) {
      for (const t of times) {
        if (time_in_range(t, u, true)) {
          if (!untilMap[u]) untilMap[u] = []
          untilMap[u].push([room, t[1]])
        }
      }
    }
  }

  const to_seconds_relative = (t) => {
    const s = to_seconds(t);
    return s == 0 ? s + seconds_in_day : s;
  }

  for (const [room, times] of todayBookings) {
    for (const t of times) {
      if (time_in_range(t, now)) {
        const cnt = globalCounter++;
        const thenTimes = untilMap[t[1]]?.sort(([_, t1], [__, t2]) => to_seconds_relative(t2) - to_seconds_relative(t1))
        console.log(untilMap)
        const thenTimesRepr = thenTimes?.map(([r, t]) => `<span class='thenRoom'>${r}</span> till <span class='thenEndTime'>${t}</span>`)
        const thenStr = thenTimesRepr?.join("<br>");
        const thenFinal = thenStr || "Nowhere";
        const id = `then-${cnt}`;
        const btnId = `btn-${id}`;
        const thenHTML = `<button id='${btnId}' onclick="changeShownHidden('${id}', '${btnId}')">Show places to go after</button><div style="display:none" id="then-${cnt}">${thenFinal}</div>`
        free_now.push([room, t, thenHTML])
      }
    }
  }

  free_now.sort(([r1, t1, __1], [r2, t2, __2]) => {
    return to_seconds_relative(t1[1]) - to_seconds_relative(t2[1]);
  })

  console.log(free_now)

  // free_now.sort(([r1, t1, __1], [r2, t2, __2]) => {
  //   const inHuxley1 = r1.indexOf("HXLY") !== -1;
  //   const inHuxley2 = r2.indexOf("HXLY") !== -1;

  //   if ((inHuxley1 && inHuxley2) || (!inHuxley1 && !inHuxley2)) {
  //     return to_seconds_relative(t2[1]) - to_seconds_relative(t1[1]);
  //   } else {
  //     return inHuxley1 ? -1 : 1;
  //   }
  // });

  return free_now;
}