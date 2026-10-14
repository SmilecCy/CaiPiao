const $ = (id) => document.getElementById(id);

const shakeBtn = $("shakeBtn");
const clearBtn = $("clearBtn");
const countInput = $("countInput");
const redMachine = $("redMachine");
const blueMachine = $("blueMachine");
const redBallsArea = $("redBallsArea");
const blueBallsArea = $("blueBallsArea");
const redResult = $("redResult");
const blueResult = $("blueResult");
const historyList = $("historyList");
const historyCount = $("historyCount");
const drawsList = $("drawsList");
const drawsCount = $("drawsCount");

let rolling = false;

function getMachineSize() {
    return redMachine.offsetWidth || 200;
}

function createBall(value, type, area) {
    const ms = getMachineSize();
    const ball = document.createElement("div");
    ball.className = `ball ${type}`;
    ball.textContent = String(value).padStart(2, "0");
    ball.style.left = "50%";
    ball.style.top = "50%";
    ball.style.marginLeft = `-${ms * 0.075}px`;
    ball.style.marginTop = `-${ms * 0.075}px`;
    const radius = ms * (0.12 + Math.random() * 0.22);
    const duration = 1.0 + Math.random() * 1.2;
    const delay = -Math.random() * duration;
    const reverse = Math.random() > 0.5 ? "reverse" : "normal";
    ball.style.setProperty("--r", `${radius}px`);
    ball.style.animationDuration = `${duration}s`;
    ball.style.animationDelay = `${delay}s`;
    ball.style.animationDirection = reverse;
    area.appendChild(ball);
    return ball;
}

function generateStackPositions(count) {
    const ms = getMachineSize();
    const positions = [];
    const baseY = ms * 0.9;
    const size = ms * 0.135;
    let remaining = count;
    let layer = 0;
    while (remaining > 0) {
        const perLayer = Math.min(remaining, Math.max(1, 5 - layer));
        const y = baseY - layer * (size - ms * 0.015);
        const offset = layer % 2 === 1 ? size / 2 : 0;
        const startX = ms / 2 - ((perLayer - 1) * size) / 2 + offset;
        for (let i = 0; i < perLayer; i++) {
            positions.push({
                x: startX + i * size + (Math.random() * ms * 0.02 - ms * 0.01),
                y: y + (Math.random() * ms * 0.015 - ms * 0.0075),
            });
        }
        remaining -= perLayer;
        layer++;
    }
    return positions;
}

function createStaticBall(value, type, area, pos) {
    const ms = getMachineSize();
    const ball = document.createElement("div");
    ball.className = `ball ${type}`;
    ball.textContent = String(value).padStart(2, "0");
    ball.style.left = `${pos.x}px`;
    ball.style.top = `${pos.y}px`;
    ball.style.marginLeft = `-${ms * 0.075}px`;
    ball.style.marginTop = `-${ms * 0.075}px`;
    area.appendChild(ball);
    return ball;
}

function setupStaticBalls() {
    redBallsArea.innerHTML = "";
    blueBallsArea.innerHTML = "";
    const redPositions = generateStackPositions(12);
    redPositions.forEach((pos) => {
        const v = Math.floor(Math.random() * 33) + 1;
        createStaticBall(v, "red", redBallsArea, pos);
    });
    const bluePositions = generateStackPositions(6);
    bluePositions.forEach((pos) => {
        const v = Math.floor(Math.random() * 16) + 1;
        createStaticBall(v, "blue", blueBallsArea, pos);
    });
}

function startRolling() {
    redMachine.classList.add("shaking");
    blueMachine.classList.add("shaking");
    redBallsArea.innerHTML = "";
    blueBallsArea.innerHTML = "";

    for (let i = 0; i < 12; i++) {
        const v = Math.floor(Math.random() * 33) + 1;
        const ball = createBall(v, "red", redBallsArea);
        ball.classList.add("rolling");
        ball.style.animationDelay = `${i * 0.05}s`;
    }
    for (let i = 0; i < 6; i++) {
        const v = Math.floor(Math.random() * 16) + 1;
        const ball = createBall(v, "blue", blueBallsArea);
        ball.classList.add("rolling");
        ball.style.animationDelay = `${i * 0.05}s`;
    }
}

function stopRolling() {
    redMachine.classList.remove("shaking");
    blueMachine.classList.remove("shaking");
    setupStaticBalls();
}

function showResults(tickets) {
    redResult.innerHTML = "";
    blueResult.innerHTML = "";

    const firstTicket = tickets[0];
    firstTicket.red.forEach((num, i) => {
        setTimeout(() => {
            const ball = document.createElement("div");
            ball.className = "result-ball red";
            ball.textContent = String(num).padStart(2, "0");
            redResult.appendChild(ball);
        }, i * 200);
    });

    setTimeout(() => {
        const ball = document.createElement("div");
        ball.className = "result-ball blue";
        ball.textContent = String(firstTicket.blue).padStart(2, "0");
        blueResult.appendChild(ball);
    }, firstTicket.red.length * 200);

    if (tickets.length > 1) {
        const extra = document.createElement("div");
        extra.style.cssText = "color:#7f8c8d;font-size:0.85rem;margin-top:8px;width:100%;text-align:center;";
        extra.textContent = `共生成 ${tickets.length} 注，详情见下方历史记录`;
        setTimeout(() => {
            redResult.appendChild(extra);
        }, firstTicket.red.length * 200 + 300);
    }
}

async function generate() {
    if (rolling) return;
    rolling = true;
    shakeBtn.disabled = true;

    const count = parseInt(countInput.value, 10) || 1;
    startRolling();

    await new Promise((r) => setTimeout(r, 1500));

    try {
        const resp = await fetch(`/api/generate?count=${count}`, { method: "POST" });
        if (!resp.ok) throw new Error("生成失败");
        const data = await resp.json();
        stopRolling();
        showResults(data.tickets);
        await loadHistory();
    } catch (err) {
        stopRolling();
        alert("号码生成失败，请重试");
    } finally {
        rolling = false;
        shakeBtn.disabled = false;
    }
}

function renderHistory(records) {
    historyCount.textContent = `${records.length} 条`;
    if (records.length === 0) {
        historyList.innerHTML = '<div class="empty-hint">暂无记录，点击「欢乐摇一摇」开始吧～</div>';
        return;
    }

    const groups = [];
    const groupMap = new Map();
    records.forEach((rec, idx) => {
        const key = rec.batch || `legacy-${idx}`;
        if (!groupMap.has(key)) {
            const group = { time: rec.time, items: [] };
            groupMap.set(key, group);
            groups.push(group);
        }
        groupMap.get(key).items.push(rec);
    });

    historyList.innerHTML = groups
        .slice()
        .reverse()
        .map((group) => {
            const isMulti = group.items.length > 1;
            const rows = group.items
                .map((rec, rowIdx) => {
                    const timeCell = rowIdx === 0
                        ? `<span class="history-time">${group.time || ""}</span>`
                        : `<span class="history-time history-time-empty"></span>`;
                    const balls = (rec.red || [])
                        .map((n) => `<span class="history-ball red">${String(n).padStart(2, "0")}</span>`)
                        .join("") + `<span class="history-ball blue">${String(rec.blue).padStart(2, "0")}</span>`;
                    const prize = rec.prize || { name: "未开奖", level: 0 };
                    const prizeName = prize.name || "未开奖";
                    const prizeLevel = prize.level || 0;
                    const prizeClass = prizeLevel > 0 ? `prize-tag prize-${prizeLevel}` : "prize-tag prize-none";
                    const drawCode = rec.matched_draw ? rec.matched_draw.code : "";
                    const prizeTip = drawCode ? `匹配第 ${drawCode} 期开奖 · 命中 ${prize.red_hit || 0} 红${prize.blue_hit ? "+1蓝" : ""}` : "暂无对应开奖数据";
                    return `<div class="history-row">${timeCell}<div class="history-balls">${balls}</div><span class="${prizeClass}" title="${prizeTip}">${prizeName}</span></div>`;
                })
                .join("");
            const badge = isMulti ? `<span class="batch-badge">${group.items.length} 注</span>` : "";
            return `<div class="history-item">${badge}${rows}</div>`;
        })
        .join("");
}

async function loadHistory() {
    try {
        const resp = await fetch("/api/history");
        const data = await resp.json();
        renderHistory(data.records);
    } catch (err) {
        console.error("加载历史失败", err);
    }
}

async function clearHistory() {
    if (!confirm("确定要清空全部历史记录吗？")) return;
    try {
        await fetch("/api/history", { method: "DELETE" });
        await loadHistory();
    } catch (err) {
        alert("清空失败，请重试");
    }
}

function renderDraws(draws) {
    drawsCount.textContent = `${draws.length} 期`;
    if (draws.length === 0) {
        drawsList.innerHTML = '<div class="empty-hint">暂无开奖数据</div>';
        return;
    }
    drawsList.innerHTML = draws
        .map((d) => {
            const redBalls = (d.red || [])
                .map((n) => `<span class="draw-ball red">${String(n).padStart(2, "0")}</span>`)
                .join("");
            const blueBall = `<span class="draw-ball blue">${String(d.blue).padStart(2, "0")}</span>`;
            return `
                <div class="draw-item">
                    <div class="draw-item-header">
                        <span class="draw-code">第 ${d.code} 期</span>
                        <span class="draw-date">${d.date}</span>
                    </div>
                    <div class="draw-balls">${redBalls}${blueBall}</div>
                </div>
            `;
        })
        .join("");
}

async function loadDraws() {
    try {
        const resp = await fetch("/api/draws?count=8");
        if (!resp.ok) throw new Error("获取开奖数据失败");
        const data = await resp.json();
        renderDraws(data.draws || []);
    } catch (err) {
        console.error("加载开奖数据失败", err);
        drawsCount.textContent = "加载失败";
        drawsList.innerHTML = '<div class="empty-hint">开奖数据加载失败，请稍后重试</div>';
    }
}

shakeBtn.addEventListener("click", generate);
clearBtn.addEventListener("click", clearHistory);

let resizeTimer;
window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        if (!rolling) setupStaticBalls();
    }, 150);
});

setupStaticBalls();
loadHistory();
loadDraws();