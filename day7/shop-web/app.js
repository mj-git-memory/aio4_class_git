const $ = (selector) => document.querySelector(selector);
const modes = {
  sync: {
    name: "동기 · 순차", sub: "def + httpx.Client", expected: 2.7, responsive: true,
    title: "하나가 끝나면 다음 요청을 보냅니다.",
    desc: "재고 → 배송 → 리뷰 순서입니다. 일반 동기 함수는 작업 스레드에서 실행하므로 서버의 이벤트 루프는 유지됩니다.",
    code: `def load_product(client):
    stock = client.get('/api/service/stock')
    delivery = client.get('/api/service/delivery')
    reviews = client.get('/api/service/reviews')

# 실험 서버에서는 위 동기 함수를 스레드에 맡김
result = await asyncio.to_thread(load_product, client)`
  },
  await: {
    name: "비동기 · 순차", sub: "await를 하나씩", expected: 2.7, responsive: true,
    title: "비동기 함수여도 순서대로 기다릴 수 있어요.",
    desc: "첫 응답을 받은 뒤 다음 요청을 시작합니다. 총 대기는 합쳐지지만, 기다리는 동안 다른 사용자 요청을 처리할 수 있습니다.",
    code: `async def load_product(client):
    stock = await client.get('/api/service/stock')
    delivery = await client.get('/api/service/delivery')
    reviews = await client.get('/api/service/reviews')

# AsyncClient여도 세 요청을 함께 시작하지 않음`
  },
  gather: {
    name: "비동기 · 동시", sub: "asyncio.gather()", expected: 1.2, responsive: true,
    title: "독립적인 세 요청의 대기 시간을 겹칩니다.",
    desc: "세 요청을 함께 진행하고 모두 끝나면 결과를 받습니다. 전체 시간은 가장 오래 걸리는 리뷰 요청에 가까워집니다.",
    code: `async def load_product(client):
    results = await asyncio.gather(
        client.get('/api/service/stock'),
        client.get('/api/service/delivery'),
        client.get('/api/service/reviews'),
    )
    return results  # 전달한 순서대로 결과 반환`
  },
  tasks: {
    name: "Task · 동시", sub: "먼저 등록, 나중에 await", expected: 1.2, responsive: true,
    title: "gather() 없이도 함께 진행할 수 있습니다.",
    desc: "create_task()로 세 작업을 모두 등록한 다음 기다립니다. await를 순서대로 적어도 이미 등록된 나머지 작업이 함께 진행됩니다.",
    code: `stock = asyncio.create_task(client.get('/api/service/stock'))
delivery = asyncio.create_task(client.get('/api/service/delivery'))
reviews = asyncio.create_task(client.get('/api/service/reviews'))

results = [await stock, await delivery, await reviews]
# 모두 등록한 뒤 기다리는 순서가 중요!`
  },
  blocking: {
    name: "잘못된 비동기", sub: "async 안의 time.sleep", expected: 2.7, responsive: false,
    title: "함께 요청해도 서버가 막히면 기다립니다.",
    desc: "클라이언트는 gather()로 요청하지만, API가 time.sleep()을 직접 호출합니다. 같은 이벤트 루프의 다른 요청도 지연됩니다.",
    code: `# 클라이언트: gather()로 세 요청을 함께 보냄
# 서버의 API: 아래처럼 처리 (의도적인 문제)
@app.get('/api/service/{service}')
async def service_api(service):
    time.sleep(delay)  # 이벤트 루프 스레드를 막음
    return data

# async def를 붙였다고 자동으로 비동기가 되지 않음`
  },
  thread: {
    name: "동기 I/O 개선", sub: "asyncio.to_thread()", expected: 1.2, responsive: true,
    title: "기존 동기 I/O 함수는 별도 스레드에 맡깁니다.",
    desc: "클라이언트는 gather()를 사용합니다. 서버는 legacy_lookup()을 작업 스레드에 맡겨 이벤트 루프가 다른 요청을 처리하게 합니다.",
    code: `def legacy_lookup(delay):
    time.sleep(delay)

@app.get('/api/service/{service}')
async def service_api(service):
    await asyncio.to_thread(legacy_lookup, delay)
    return data  # 기다리는 동안 이벤트 루프는 계속 동작`
  }
};

const lessons = [
  {tab: "동기와 비동기", title: "비동기는 ‘기다리는 동안’을 활용합니다.", html: `
    <p>동기 코드는 호출한 작업이 끝나야 다음 줄로 진행합니다. 비동기 코드는 작업을 기다리는 지점에서 실행을 양보하고, 나중에 그 자리부터 이어갈 수 있습니다. 이벤트 루프가 준비된 작업들을 번갈아 진행합니다.</p>
    <table><thead><tr><th>구분</th><th>현재 작업의 대기</th><th>이 실험의 예</th></tr></thead><tbody><tr><td>동기</td><td>호출한 스레드가 기다림</td><td>httpx.Client.get()</td></tr><tr><td>비동기</td><td>현재 코루틴은 기다리고, 이벤트 루프는 다른 작업 진행 가능</td><td>await httpx.AsyncClient.get()</td></tr></tbody></table>
    <h4>순차 실행과 동시 진행은 별도의 선택입니다</h4><p><code>async def</code> 안에서 <code>await A()</code> 다음 <code>await B()</code>를 쓰면 A가 끝난 뒤 B를 시작합니다. A와 B의 대기를 겹치려면 둘을 함께 진행하도록 등록해야 합니다.</p>
    <p class="callout">비동기 ≠ 여러 CPU에서 동시 계산. 이 앱은 단일 이벤트 루프에서 I/O 대기를 겹칩니다. 화면의 타이머는 브라우저에서 동작하므로 서버가 막혀도 계속 움직일 수 있습니다.</p>
    <h4>이 실험에서 무엇이 실제인가요?</h4><p>화면 → FastAPI → HTTPX → 같은 서버의 모의 API로 실제 HTTP 요청을 보냅니다. 재고 0.6초·배송 0.9초·리뷰 1.2초의 외부 응답 대기를 sleep으로 재현합니다. 타임라인은 응답 후 서버 측정값을 표시하며, 실제 쇼핑 데이터나 외부 서비스는 사용하지 않습니다.</p>`},
  {tab: "코루틴과 Task", title: "함수, 코루틴 객체, Task는 다릅니다.", html: `
    <pre>async def fetch():           # 코루틴 함수: 작업 정의
    await asyncio.sleep(1)
    return '완료'

async def main():
    work = fetch()          # 코루틴 객체 생성. 본문은 아직 실행 안 됨
    result = await work     # 실행하고 완료까지 기다림
    print(result)

asyncio.run(main())          # 일반 Python 스크립트의 진입점</pre>
    <p><strong>코루틴</strong>은 실행을 일시 중단했다가 이어갈 수 있는 작업입니다. <strong>코루틴 함수</strong>는 그 작업의 정의이고, 호출해서 만든 <strong>코루틴 객체</strong>는 한 번 실행할 작업을 나타냅니다.</p>
    <p><strong>Task</strong>는 코루틴을 이벤트 루프가 실행하도록 등록하고 상태와 결과를 관리하는 객체입니다. <code>asyncio.create_task(work)</code>로 만듭니다. 현재 코드가 실행 기회를 양보하면 등록된 작업이 진행될 수 있습니다.</p>
    <p class="callout">코루틴 객체를 만들기만 하고 기다리거나 등록하지 않으면 실행되지 않습니다. 완료된 코루틴 객체는 다시 await할 수 없지만, 완료된 Task의 결과는 다시 await해서 받을 수 있습니다.</p>
    <p>FastAPI의 <code>async def</code> 엔드포인트는 프레임워크가 실행합니다. 엔드포인트 안에서는 <code>await</code>를 사용하세요. 이미 실행 중인 이벤트 루프 안에서 <code>asyncio.run()</code>을 호출하면 오류가 납니다.</p>`},
  {tab: "문법과 실행 순서", title: "await는 ‘기다리지 않는다’는 뜻이 아닙니다.", html: `
    <table><thead><tr><th>문법</th><th>역할</th></tr></thead><tbody><tr><td><code>async def</code></td><td>코루틴 함수를 정의</td></tr><tr><td><code>await work</code></td><td>현재 코루틴에서 완료를 기다림. 미완료 작업을 기다릴 때 다른 작업에 기회를 줄 수 있음</td></tr><tr><td><code>asyncio.run(main())</code></td><td>스크립트에서 이벤트 루프를 만들고 main을 실행한 뒤 정리</td></tr><tr><td><code>await asyncio.gather(A(), B())</code></td><td>여러 작업을 함께 진행하고 입력 순서대로 결과 수집</td></tr><tr><td><code>asyncio.create_task(A())</code></td><td>코루틴을 Task로 등록</td></tr><tr><td><code>async with httpx.AsyncClient() as client</code></td><td>비동기 자원에 진입하고, 블록을 나갈 때 연결 자원을 정리</td></tr><tr><td><code>await asyncio.to_thread(fn, arg)</code></td><td>동기 함수를 별도 스레드에서 실행하고 결과 기다림</td></tr></tbody></table>
    <h4>gather()는 필수가 아닙니다</h4><pre># 순차 실행: 약 2초 + 2초 = 4초
await make_drink('커피')
await make_drink('차')

# 동시 진행: 먼저 두 작업을 등록 → 약 2초
coffee = asyncio.create_task(make_drink('커피'))
tea = asyncio.create_task(make_drink('차'))
await coffee
await tea

# 주의: 이 방식은 각 작업을 즉시 기다려서 약 4초
coffee = await asyncio.create_task(make_drink('커피'))
tea = await asyncio.create_task(make_drink('차'))</pre>
    <p class="callout"><code>async with</code> 자체가 여러 요청을 동시에 실행해 주지는 않습니다. 동시 진행 여부는 안에서 작업을 어떻게 등록하고 기다리는지에 달려 있습니다.</p>`},
  {tab: "언제 사용할까?", title: "독립적인 I/O 요청이 여러 개일 때 유용합니다.", html: `
    <p>상품 상세 화면의 재고·배송·리뷰처럼 서로의 결과가 필요 없는 API 조회는 대기를 겹칠 수 있습니다. 다른 예로 여러 페이지 수집, 비동기 DB 조회, 여러 사용자를 받는 웹서버가 있습니다.</p>
    <table><thead><tr><th>상황</th><th>선택</th></tr></thead><tbody><tr><td>독립적인 API 조회 여러 개</td><td>AsyncClient + gather 또는 Task</td></tr><tr><td>앞 요청의 결과가 있어야 다음 요청 가능</td><td>await로 순차 실행. 예: 로그인 후 받은 토큰으로 내 정보 조회</td></tr><tr><td>기존 동기 I/O 라이브러리만 사용 가능</td><td>to_thread 검토. 스레드 안전성과 동시 실행 개수도 고려</td></tr><tr><td>큰 계산·이미지 처리 등 CPU 작업</td><td>별도 프로세스나 작업 큐 검토. asyncio만으로 빨라지지 않음</td></tr></tbody></table>
    <h4>FastAPI의 def와 async def</h4><p>FastAPI는 일반 <code>def</code> 엔드포인트를 스레드풀에서 실행합니다. <code>async def</code> 엔드포인트는 이벤트 루프에서 실행합니다. 단, async 함수 안에서 직접 호출한 일반 함수까지 자동으로 스레드풀에 보내지는 않습니다.</p>
    <p>이 앱의 ‘동기 · 순차’는 동기 클라이언트 전체를 <code>to_thread()</code>로 실행합니다. 세 요청은 순차 실행이지만 이벤트 루프는 응답할 수 있습니다. ‘잘못된 비동기’는 서버의 이벤트 루프에서 동기 함수를 직접 호출하므로 다른 요청도 지연됩니다.</p>
    <p class="callout">실무에서는 동시 요청 수 제한, 타임아웃, 실패 처리도 필요합니다. 이 실험은 세 요청만 사용하고 HTTPX 타임아웃은 20초로 설정했습니다.</p>`},
  {tab: "겪었던 오류들", title: "오류가 발생한 단계를 먼저 구분하세요.", html: `
    <h4>① 일반 def 안에서 await 사용</h4><pre># 오류
def request_one(client):
    response = await client.get('/health')

# 수정: AsyncClient를 전달하는 코루틴 함수로 정의
async def request_one(client):
    response = await client.get('/health')</pre>
    <h4>② httpx.ConnectError: All connection attempts failed</h4><p>서버에 연결하기 전에 실패했습니다. 서버가 켜져 있는지, 요청 주소와 서버 포트가 같은지 확인하세요. <code>probe.py</code>는 요청을 보내는 클라이언트이며, 실행한다고 서버가 자동으로 켜지지 않습니다.</p>
    <h4>③ address already in use</h4><p>같은 포트를 다른 프로세스가 사용 중입니다. 기존 서버의 터미널에서 <kbd>Ctrl + C</kbd>로 종료하거나 다른 포트를 사용하세요.</p><pre>lsof -nP -iTCP:8010 -sTCP:LISTEN
python -m uvicorn day7.shop_lab:app --port 8011</pre><p>포트를 바꾸면 브라우저도 <code>http://127.0.0.1:8011</code>로 접속하세요. 이 앱의 내부 요청은 접속한 서버 포트를 자동으로 사용합니다.</p>
    <h4>④ 응답은 받았는데 HTTP 오류</h4><p><code>response.raise_for_status()</code>는 상태 코드를 반환하는 함수가 아니라 성공 범위를 벗어난 응답에 예외를 발생시키는 함수입니다. 상태 코드는 <code>response.status_code</code>로 읽습니다. 200 성공이어도 응답이 느릴 수 있습니다.</p>
    <p class="callout">‘잘못된 비동기’가 느린 이유는 time.sleep()의 이벤트 루프 차단입니다. ConnectError는 서버 연결 실패입니다. 서로 다른 원인입니다.</p>`}
];

let selected = "gather";
let busy = false;
let batch = false;
let healthBusy = false;
const history = [];
const serviceNames = { stock: "재고", delivery: "배송", reviews: "리뷰" };

$("#modes").innerHTML = Object.entries(modes).map(([key, value]) =>
  `<button data-mode="${key}" aria-pressed="false">${value.name}<small>${value.sub}</small></button>`
).join("");

function selectMode(key) {
  selected = key;
  const mode = modes[key];
  $("#mode-title").textContent = mode.title;
  $("#mode-desc").textContent = mode.desc;
  $("#code").textContent = mode.code;
  $("#code-mode").textContent = key.toUpperCase();
  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.mode === key));
  });
}

function lock(locked) {
  busy = locked;
  document.querySelectorAll("#modes button, #run, #compare, #scale").forEach((button) => {
    button.disabled = locked;
  });
}

function setStatus(message, error = false) {
  $("#status").textContent = message;
  $("#status").classList.toggle("error", error);
}

async function getJSON(path) {
  const response = await fetch(path, {cache: "no-store", signal: AbortSignal.timeout(60000)});
  if (!response.ok) throw new Error(`HTTP ${response.status}: API 응답을 확인하세요.`);
  return response.json();
}

function renderResult(data) {
  $("#elapsed").textContent = data.elapsed.toFixed(2);
  $("#timeline-note").textContent = `${modes[data.mode].name} · ${data.scale}× · 막대는 각 API가 서버에 도착한 뒤 완료될 때까지의 구간입니다. 전체 시간에는 HTTP 연결·응답 처리도 포함됩니다.`;
  $("#service-cards").classList.remove("loading");
  data.results.forEach((result, i) => {
    $("#service-cards").children[i].querySelector("strong").textContent = result.value;
  });
  const max = Math.max(data.elapsed, ...data.results.map((result) => result.end));
  const timeline = $("#timeline");
  timeline.replaceChildren();
  data.results.forEach((result) => {
    const row = document.createElement("div");
    row.className = "timeline-row";
    const label = document.createElement("span");
    label.textContent = serviceNames[result.service];
    const track = document.createElement("div");
    track.className = "track";
    const bar = document.createElement("div");
    bar.className = "bar";
    bar.style.left = `${result.start / max * 100}%`;
    bar.style.width = `${(result.end - result.start) / max * 100}%`;
    bar.title = `${result.start.toFixed(3)}초 시작 → ${result.end.toFixed(3)}초 종료`;
    track.append(bar);
    const time = document.createElement("small");
    time.textContent = `${(result.end - result.start).toFixed(2)}초`;
    row.append(label, track, time);
    timeline.append(row);
  });
  const axis = document.createElement("div");
  axis.className = "axis";
  for (const value of [0, max / 2, max]) {
    const tick = document.createElement("span");
    tick.textContent = `${value.toFixed(2)}초`;
    axis.append(tick);
  }
  timeline.append(axis);
  history.unshift(data);
  // 메모리와 표 길이를 제한한다.
  history.splice(30);
  $("#history").innerHTML = history.map((item) => {
    const mode = modes[item.mode];
    return `<tr><td>${mode.name}</td><td>${item.scale}×</td><td>약 ${(mode.expected * item.scale).toFixed(1)}초</td><td><strong>${item.elapsed.toFixed(2)}초</strong></td><td>${mode.responsive ? "처리 가능" : "이벤트 루프 차단"}*</td></tr>`;
  }).join("");
  $("#timeline-note").textContent += " *표의 다른 요청 상태는 코드 구조에 따른 설명이며, 실측은 ‘서버 응답 확인’으로 확인하세요.";
}

async function runMode(mode) {
  selectMode(mode);
  const scale = Number($("#scale").value);
  const started = performance.now();
  $("#service-cards").classList.add("loading");
  for (const card of $("#service-cards").children) card.querySelector("strong").textContent = "응답을 기다리고 있어요…";
  $("#elapsed").textContent = "…";
  $("#timeline").innerHTML = '<p class="empty">실제 API 요청 중 · 완료 후 이번 측정의 타임라인이 표시됩니다.</p>';
  $("#timeline-note").textContent = "대기 중 ‘서버 응답 확인’을 눌러 보세요. 아래 경과 시간은 브라우저에서 측정합니다.";
  const timer = setInterval(() => setStatus(`${batch ? "전체 비교 중 · " : ""}${modes[mode].name} · 브라우저 경과 ${((performance.now() - started) / 1000).toFixed(1)}초`), 100);
  try {
    const data = await getJSON(`/api/run?mode=${mode}&scale=${scale}`);
    renderResult(data);
    return data;
  } catch (error) {
    $("#service-cards").classList.remove("loading");
    for (const card of $("#service-cards").children) card.querySelector("strong").textContent = "불러오기 실패 · 다시 실행해 주세요";
    $("#elapsed").textContent = "—";
    $("#timeline").innerHTML = '<p class="empty">측정 실패 · 서버 실행 상태와 터미널 로그를 확인하세요.</p>';
    throw error;
  } finally {
    clearInterval(timer);
  }
}

async function execute(all = false) {
  if (busy) return;
  lock(true);
  batch = all;
  try {
    if (all) {
      for (const mode of Object.keys(modes)) await runMode(mode);
      setStatus("6가지 비교 완료 · 같은 배율의 실제 측정 시간을 표에서 비교하세요.");
    } else {
      const data = await runMode(selected);
      setStatus(`완료 · ${modes[data.mode].name} · 서버 측정 ${data.elapsed.toFixed(2)}초`);
    }
  } catch (error) {
    setStatus(`요청 실패: ${error.message} 서버가 켜져 있는지, 현재 주소가 맞는지 확인하세요.`, true);
  } finally {
    batch = false;
    lock(false);
  }
}

$("#modes").addEventListener("click", (event) => {
  const button = event.target.closest("[data-mode]");
  if (button && !busy) selectMode(button.dataset.mode);
});
$("#run").addEventListener("click", () => execute());
$("#compare").addEventListener("click", () => execute(true));
$("#health").addEventListener("click", async () => {
  if (healthBusy) return;
  healthBusy = true;
  $("#health").disabled = true;
  const started = performance.now();
  $("#health-result").textContent = "/api/health · 서버 응답을 기다리는 중…";
  try {
    await getJSON(`/api/health?t=${Date.now()}`);
    const elapsed = performance.now() - started;
    $("#health-result").textContent = `/api/health · ${elapsed.toFixed(0)}ms · 브라우저 왕복 실측${elapsed > 300 ? " · 대기 지연 관찰" : " · 응답 도착"}`;
  } catch (error) {
    $("#health-result").textContent = `응답 확인 실패: ${error.message}`;
  } finally {
    healthBusy = false;
    $("#health").disabled = false;
  }
});

$("#lesson-tabs").innerHTML = lessons.map((lesson, i) =>
  `<button role="tab" id="tab-${i}" aria-controls="lesson" aria-selected="false" tabindex="-1" data-lesson="${i}">${lesson.tab}</button>`
).join("");
function selectLesson(index, focus = false) {
  document.querySelectorAll("[data-lesson]").forEach((button, i) => {
    button.setAttribute("aria-selected", String(i === index));
    button.tabIndex = i === index ? 0 : -1;
    if (focus && i === index) button.focus();
  });
  $("#lesson").setAttribute("aria-labelledby", `tab-${index}`);
  $("#lesson").innerHTML = `<h3>${lessons[index].title}</h3>${lessons[index].html}`;
}
$("#lesson-tabs").addEventListener("click", (event) => {
  const button = event.target.closest("[data-lesson]");
  if (button) selectLesson(Number(button.dataset.lesson));
});
$("#lesson-tabs").addEventListener("keydown", (event) => {
  const index = Number(event.target.dataset.lesson);
  if (!Number.isInteger(index)) return;
  let next;
  if (event.key === "ArrowRight") next = (index + 1) % lessons.length;
  if (event.key === "ArrowLeft") next = (index + lessons.length - 1) % lessons.length;
  if (event.key === "Home") next = 0;
  if (event.key === "End") next = lessons.length - 1;
  if (next !== undefined) { event.preventDefault(); selectLesson(next, true); }
});
selectMode(selected);
selectLesson(0);
