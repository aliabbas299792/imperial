// elements in the page
const data_div = document.querySelector("#data");
const free_now_div = document.querySelector("#free_now");
const timeView = document.getElementById("viewTime");
const dateView = document.getElementById("viewDate");
const searchBtn = document.getElementById("searchTimes");
const resetTimeBtn = document.getElementById("resetTime");
const roomFilterInput = document.getElementById("roomFilter");

// constants
const seconds_in_day = 3600 * 24;

// global state
let data_obj = [];
let roomElements = [];
let globalCounter = 0;

/*
# Helper functions
*/

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

function changeShownHidden(e, id, btnId) {
  const el = document.querySelector(`#${id}`);
  const btn = document.querySelector(`#${btnId}`);
  const notShown = el.style.display != 'block';

  if(!e.target.id.startsWith("then-") && !e.target.id.startsWith("btn-then-")) {
    // only allow the button or the modal background to be clicked
    return
  }

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
        const thenTimes = untilMap[t[1]]?.sort(([_, t1], [__, t2]) => to_seconds_relative(t1) - to_seconds_relative(t2))
        const thenTimesRepr = thenTimes?.map(([r, t], idx, arr) => {
          const d = document.createElement("div");
          const thenRoom = document.createElement("span");
          thenRoom.classList.add("thenRoom");
          thenRoom.innerText = r;
          const thenEndTime = document.createElement("span");
          thenEndTime.classList.add("thenEndTime");
          thenEndTime.innerText = t;
          d.appendChild(thenRoom)
          d.appendChild(document.createTextNode(" till "))
          d.appendChild(thenEndTime)
          return d
        })

        if(!thenTimesRepr) {
          free_now.push([room, t, document.createTextNode("Nowhere")])
        } else {
          const thenDiv = document.createElement("div");
          thenTimesRepr.forEach(e => thenDiv.appendChild(e))

          const id = `then-${cnt}`;
          const btnId = `btn-${id}`;
          
          const showButton = document.createElement('button');
          showButton.id = btnId;
          showButton.textContent = 'Show places to go after';
          showButton.setAttribute('onclick', `changeShownHidden(event, '${id}', '${btnId}')`);
  
          const thenContainer = document.createElement('div');
          thenContainer.id = id;
          thenContainer.classList.add("thenModal");
          thenContainer.style.display = 'none';  // Initially hidden
          thenContainer.appendChild(thenDiv);
          thenContainer.setAttribute('onclick', `changeShownHidden(event, '${id}', '${btnId}')`);
  
          const thenOuter = document.createElement("div");
          thenOuter.appendChild(showButton);
          thenOuter.appendChild(thenContainer);
          free_now.push([room, t, thenOuter])
        }
      }
    }
  }

  free_now.sort(([r1, t1, __1], [r2, t2, __2]) => {
    return to_seconds_relative(t1[1]) - to_seconds_relative(t2[1]);
  })

  return free_now;
}

function filterElements(query) {
  const lowerCaseQuery = query.toLowerCase()
  const matchingElement = (e) => e.firstChild.innerText.toLowerCase().indexOf(lowerCaseQuery) !== -1
  roomElements.filter(e => !matchingElement(e)).forEach(e => e.style.display = 'none')
  roomElements.filter(e => matchingElement(e)).forEach(e => e.style.display = '')
}

/*
# Event Handlers
*/

window.onload = () => {
  const [date, time] = getSearchDateTime();
  timeView.value = time;
  dateView.value = date;
}


searchBtn.onclick = () => {
  window.location.href = window.location.origin + getSearchString();
}

resetTimeBtn.onclick = () => {
  dateView.value = getDateStr(new Date());
  timeView.value = timeStr(new Date());
  searchBtn.click();
}

roomFilterInput.oninput = () => {
  filterElements(roomFilterInput.value)
}

/*
# Entry point function
*/

fetch("/data")
  .then(res => res.json())
  .then(r => {
    for (const room of r) {
      const [name, days] = room;

      // make room block container
      const roomBlock = document.createElement('div');
      roomBlock.classList.add('room-block');

      // make room header
      const roomHeader = document.createElement('h2');
      roomHeader.classList.add('room');
      roomHeader.textContent = name;
      roomBlock.appendChild(roomHeader);

      for (const [date, times] of days) {
        // make date block container
        const dateBlock = document.createElement('div');
        dateBlock.classList.add('date-block');

        // make date header
        const dateHeader = document.createElement('h4');
        dateHeader.classList.add('date');
        dateHeader.textContent = date;
        dateBlock.appendChild(dateHeader);

        // make time spans for each time range
        const timeSpans = times.map(t => t.map(time => {
          const span = document.createElement('span');
          span.classList.add('time');
          span.textContent = time;
          return span;
        }).map((span, idx, arr) => {
          if (idx < arr.length - 1) {
            const separator = document.createTextNode(' to ');
            return [span, separator];
          }
          return [span];
        }).flat()
        ).map((timeSpans, idx, arr) => {
          // adds a comma between time spans
          if(idx < arr.length - 1) {
            return [...timeSpans, document.createTextNode(", ")];
          }
          return timeSpans;
        }).flat()

        // make the "Free: " text node and append times
        const freeText = document.createTextNode('Free: ');
        dateBlock.appendChild(freeText);
        timeSpans.forEach(span => dateBlock.appendChild(span));

        roomBlock.appendChild(dateBlock);
      }

      roomElements.push(roomBlock)

      data_div.appendChild(roomBlock); // Append room block to the main container
    }

    data_obj = r;
  })
  .then(() => {
    const free_now = find_a_room_now();

    for (const [room, [start, end], then] of free_now) {
      const tr = document.createElement('tr');

      const roomTd = document.createElement('td');
      roomTd.textContent = room;
      tr.appendChild(roomTd);

      // Optionally include start time here if needed

      const endTd = document.createElement('td');
      const endTimeSpan = document.createElement('span');
      endTimeSpan.classList.add('time');
      endTimeSpan.textContent = end;
      endTd.appendChild(endTimeSpan);
      tr.appendChild(endTd);

      const thenTd = document.createElement('td');
      const thenTimeSpan = document.createElement('span');
      thenTimeSpan.classList.add('thenTime');
      thenTimeSpan.appendChild(then);
      thenTd.appendChild(thenTimeSpan);
      tr.appendChild(thenTd);

      roomElements.push(tr)

      free_now_div.appendChild(tr); // Append row to the free_now table
    }
  });
