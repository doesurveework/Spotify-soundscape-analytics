let popularityChartInstance = null;

async function loadDashboard() {
  const statusDot = document.getElementById("status-dot");
  const statusText = document.getElementById("status-text");
  const emptyState = document.getElementById("empty-state");
  const emptyMessage = document.getElementById("empty-message");

  try {
    const res = await fetch("/dashboard-data");

    if (res.status === 401) {
      window.location.href = "/login";
      return;
    }

    const data = await res.json();

    if (!res.ok || data.error) {
      throw new Error(data.error || `Request failed with status ${res.status}`);
    }

    // Inform user if fallback estimates were used
    if (data.metrics?.is_fallback) {
      statusText.textContent = `analyzed ${data.tracks.length} tracks (estimated metrics)`;
    } else {
      statusText.textContent = `analyzed ${data.tracks.length} tracks`;
    }

    // Render components
    if (data.metrics) {
      renderPersonality(data.metrics);
      renderScores(data.metrics);
    }

    if (data.tracks && data.tracks.length > 0) {
      renderChart(data.tracks);
      renderTrackList(data.tracks);
    }

  } catch (err) {
    if (statusDot) statusDot.classList.add("error");
    if (statusText) statusText.textContent = "failed to load";
    if (emptyMessage) emptyMessage.textContent = err.message || "Something went wrong talking to Spotify.";
    if (emptyState) emptyState.hidden = false;
    console.error("Dashboard load failed:", err);
  }
}

function renderPersonality(metrics) {
  const personalityTypeEl = document.getElementById("personality-type");
  if (personalityTypeEl) {
    personalityTypeEl.textContent = metrics.personalityType || "Sonic Listener";
  }

  // Update equalizer bar heights dynamically
  const bars = document.querySelectorAll(".eq-bar");
  bars.forEach((bar) => {
    const feature = bar.dataset.feature;
    const value = metrics.averages?.[feature] ?? 0.5;
    const pct = Math.max(4, Math.round(value * 100)); // Floor at 4% for bar visibility

    requestAnimationFrame(() => {
      const fillSpan = bar.querySelector("span");
      if (fillSpan) fillSpan.style.height = pct + "%";
    });
  });
}

function renderScores(metrics) {
  const obscurityScoreEl = document.getElementById("obscurity-score");
  const avgEnergyEl = document.getElementById("avg-energy");
  const avgDanceEl = document.getElementById("avg-dance");
  const avgValenceEl = document.getElementById("avg-valence");

  if (obscurityScoreEl) obscurityScoreEl.textContent = metrics.obscurityScore ?? "—";
  if (avgEnergyEl) avgEnergyEl.textContent = metrics.averages?.energy ?? "—";
  if (avgDanceEl) avgDanceEl.textContent = metrics.averages?.danceability ?? "—";
  if (avgValenceEl) avgValenceEl.textContent = metrics.averages?.valence ?? "—";
}

function renderChart(tracks) {
  const canvas = document.getElementById("popularity-chart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const labels = tracks.map((t) => t.name);
  const values = tracks.map((t) => t.popularity ?? 0);

  // Destroy previous Chart.js instance to prevent overlapping instances
  if (popularityChartInstance) {
    popularityChartInstance.destroy();
  }

  popularityChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: "#F2A93B",
          borderRadius: 4,
          maxBarThickness: 22,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          ticks: { display: false },
          grid: { display: false },
        },
        y: {
          min: 0,
          max: 100,
          ticks: { color: "#6B7280", font: { family: "JetBrains Mono", size: 10 } },
          grid: { color: "rgba(236,233,226,0.08)" },
        },
      },
    },
  });
}

function renderTrackList(tracks) {
  const list = document.getElementById("tracklist");
  if (!list) return;

  list.innerHTML = "";

  tracks.forEach((track, index) => {
    const li = document.createElement("li");
    li.className = "track-row";

    const art = track.album?.images?.[2]?.url || track.album?.images?.[0]?.url || "";
    const artistNames = (track.artists || []).map((a) => a.name).join(", ");
    const popularity = track.popularity !== undefined ? track.popularity : "—";

    li.innerHTML = `
      <span class="track-index">${index + 1}</span>
      <img class="track-art" src="${art}" alt="" loading="lazy">
      <div class="track-meta">
        <div class="track-name">${escapeHtml(track.name)}</div>
        <div class="track-artist">${escapeHtml(artistNames)}</div>
      </div>
      <div class="track-popularity">${popularity}</div>
    `;
    list.appendChild(li);
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}


loadDashboard();



///* Soundscape dashboard — fetches /dashboard-data and renders the page. */
//
//async function loadDashboard() {
//  const statusDot = document.getElementById("status-dot");
//  const statusText = document.getElementById("status-text");
//  const emptyState = document.getElementById("empty-state");
//  const emptyMessage = document.getElementById("empty-message");
//
//  try {
//    const res = await fetch("/dashboard-data");
//
//    if (res.status === 401) {
//      window.location.href = "/login";
//      return;
//    }
//
//    const data = await res.json();
//
//    if (!res.ok || data.error) {
//      throw new Error(data.error || `Request failed with status ${res.status}`);
//    }
//
//    // --- NEW FALLBACK CHECK ---
//    // Safely check if audio features/metrics contain fallback data
//    if (data.metrics?.is_fallback || data.audio_features?.some(f => f.is_fallback)) {
//      console.warn("Spotify API restricted audio features. Using fallback metrics.");
//
//      // Optional: Update status text to inform the user
//      statusText.textContent = `analyzed ${data.tracks.length} tracks (estimated metrics)`;
//    } else {
//      statusText.textContent = `analyzed ${data.tracks.length} tracks`;
//    }
//
//    // Render your UI as normal
//    if (data.metrics) {
//      renderPersonality(data.metrics);
//      renderScores(data.metrics);
//    }
//
//    renderChart(data.tracks);
//    renderTrackList(data.tracks);
//
//  } catch (err) {
//    statusDot.classList.add("error");
//    statusText.textContent = "failed to load";
//    emptyMessage.textContent = err.message || "Something went wrong talking to Spotify.";
//    emptyState.hidden = false;
//    console.error("Dashboard load failed:", err);
//  }
//}
//
//function renderPersonality(metrics) {
//  document.getElementById("personality-type").textContent = metrics.personalityType;
//
//  // Signature equalizer bars: map each 0–1 audio feature to a bar height %.
//  const bars = document.querySelectorAll(".eq-bar");
//  bars.forEach((bar) => {
//    const feature = bar.dataset.feature;
//    const value = metrics.averages[feature] ?? 0;
//    const pct = Math.max(4, Math.round(value * 100)); // floor at 4% so bar is visible
//    // rAF ensures the CSS transition animates in from the initial 4% height
//    requestAnimationFrame(() => {
//      bar.querySelector("span").style.height = pct + "%";
//    });
//  });
//}
//
//function renderScores(metrics) {
//  document.getElementById("obscurity-score").textContent = metrics.obscurityScore;
//  document.getElementById("avg-energy").textContent = metrics.averages.energy;
//  document.getElementById("avg-dance").textContent = metrics.averages.danceability;
//  document.getElementById("avg-valence").textContent = metrics.averages.valence;
//}
//
//function renderChart(tracks) {
//  const ctx = document.getElementById("popularity-chart");
//  const labels = tracks.map((t) => t.name);
//  const values = tracks.map((t) => t.popularity);
//
//  new Chart(ctx, {
//    type: "bar",
//    data: {
//      labels,
//      datasets: [
//        {
//          data: values,
//          backgroundColor: "#F2A93B",
//          borderRadius: 4,
//          maxBarThickness: 22,
//        },
//      ],
//    },
//    options: {
//      responsive: true,
//      plugins: { legend: { display: false } },
//      scales: {
//        x: {
//          ticks: { display: false },
//          grid: { display: false },
//        },
//        y: {
//          min: 0,
//          max: 100,
//          ticks: { color: "#6B7280", font: { family: "JetBrains Mono", size: 10 } },
//          grid: { color: "rgba(236,233,226,0.08)" },
//        },
//      },
//    },
//  });
//}
//
//function renderTrackList(tracks) {
//  const list = document.getElementById("tracklist");
//  list.innerHTML = "";
//
//  tracks.forEach((track) => {
//    const li = document.createElement("li");
//    li.className = "track-row";
//
//    const art = track.album?.images?.[2]?.url || track.album?.images?.[0]?.url || "";
//    const artistNames = (track.artists || []).map((a) => a.name).join(", ");
//
//    li.innerHTML = `
//      <img class="track-art" src="${art}" alt="" loading="lazy">
//      <div class="track-meta">
//        <div class="track-name">${escapeHtml(track.name)}</div>
//        <div class="track-artist">${escapeHtml(artistNames)}</div>
//      </div>
//      <div class="track-popularity">${track.popularity}</div>
//    `;
//    list.appendChild(li);
//  });
//}
//
//function escapeHtml(str) {
//  const div = document.createElement("div");
//  div.textContent = str ?? "";
//  return div.innerHTML;
//}
//
//loadDashboard();

/* Soundscape Dashboard Controller */


