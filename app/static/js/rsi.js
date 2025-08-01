// app/static/js/rsi.js

// Global
const activeCharts = {};  // token_interval -> {chart, timerId}

// Lưu & khôi phục
function saveChartsToStorage() {
  localStorage.setItem("activeCharts", JSON.stringify(Object.keys(activeCharts)));
}

async function restoreChartsFromStorage() {
  const saved = localStorage.getItem("activeCharts");
  if (!saved) return;

  const keys = JSON.parse(saved);

  for (const key of keys) {
    const [token, interval] = key.split("_");
    await addRSIChart(token, parseInt(interval));  // await để vẽ tuần tự
  }
}

async function loadHistoryAndDraw(token, interval, chart) {
  try {
    const res = await fetch(`/rsi_history?token=${token}&interval=${interval}`);
    const history = await res.json();

    if (!Array.isArray(history)) return;

    for (const [ts, val] of history) {
      const label = new Date(ts * 1000).toLocaleTimeString();
      chart.data.labels.push(label);
      chart.data.datasets[0].data.push(val);
    }

    chart.update();
  } catch (err) {
    console.error(`❌ Không thể tải dữ liệu RSI cũ cho ${token}:`, err);
  }
}



// Tạo chart object riêng biệt
function createEmptyRSIChart(token, interval) {
  const key = `${token}_${interval}`;
  const container = document.getElementById("rsiCharts");

  const chartDiv = document.createElement("div");
  chartDiv.className = "rsi-card";
  chartDiv.id = `chart-${key}`;
  chartDiv.innerHTML = `
    <h4>${token} - RSI ${interval}s 
      <button onclick="removeChart('${key}')">❌</button>
    </h4>
    <canvas id="canvas-${key}" height="100"></canvas>
  `;
  container.appendChild(chartDiv);

  const ctx = document.getElementById(`canvas-${key}`).getContext('2d');
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'RSI14',
        data: [],
        borderColor: getRandomColor(),
        tension: 0.2
      }]
    },
    options: {
      animation: false,
      scales: {
        y: {
          min: 0,
          max: 100
        }
      }
    }
  });

  return chart;
}

// Hàm cập nhật chart
async function updateRSIChart(token, interval, chart) {
  try {
    const res = await fetch(`/rsi?tokens=${token}&interval=${interval}`);
    const data = await res.json();
    const rsiValue = data[token]?.[`rsi_${interval}s`];

    if (rsiValue === undefined) {
      console.warn(`⚠️ No RSI data for ${token} (${interval}s)`);
      return;
    }

    // Thêm dữ liệu mới vào chart
    chart.data.labels.push(new Date().toLocaleTimeString());
    chart.data.datasets[0].data.push(rsiValue);

    // Giới hạn hiển thị 100 điểm
    if (chart.data.datasets[0].data.length > 100) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }

    chart.update();
  } catch (err) {
    console.error(`❌ Error updating ${token} (${interval}s):`, err);
  }
}

// Hàm thêm chart mới
async function addRSIChart(token, interval = 60) {
  const key = `${token}_${interval}`;
  if (activeCharts[key]) return;

  const chart = createEmptyRSIChart(token, interval);
  activeCharts[key] = { chart, timerId: null }; // Khởi tạo trước

  await loadHistoryAndDraw(token, interval, chart); // Đợi vẽ dữ liệu history

  const timerId = setInterval(
    () => updateRSIChart(token, interval, chart),
    interval * 1000
  );

  activeCharts[key].timerId = timerId;
  saveChartsToStorage();

  return chart;
}


// Hàm phụ trợ tạo màu ngẫu nhiên
function getRandomColor() {
  return `#${Math.floor(Math.random()*16777215).toString(16)}`;
}

// Xóa chart
async function removeChart(key) {
  const obj = activeCharts[key];
  if (!obj) return;

  // Gọi API backend để hủy subscribe
  try {
    const [token, interval] = key.split('_');
    await fetch(`/unsubscribe?token=${token}`);
  } catch (err) {
    console.error("❌ Lỗi khi hủy subscribe:", err);
  }

  // Xóa chart
  clearInterval(obj.timerId);
  obj.chart.destroy();
  document.getElementById(`chart-${key}`)?.remove();
  delete activeCharts[key];
  saveChartsToStorage();
}

// Khôi phục chart khi load
window.onload = restoreChartsFromStorage;
