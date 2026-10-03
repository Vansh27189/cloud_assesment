// CloudPulse Microservice - Interactive Client Dashboard

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const statusIndicator = document.getElementById('status-indicator');
  const nodePill = document.getElementById('node-pill');
  const envPill = document.getElementById('env-pill');
  const statRequests = document.getElementById('stat-requests');
  const statLatency = document.getElementById('stat-latency');
  const statMemory = document.getElementById('stat-memory');
  const statTasks = document.getElementById('stat-tasks');

  // Text Analyzer Elements
  const analyzeBtn = document.getElementById('analyze-btn');
  const textInput = document.getElementById('text-input');
  const resultCard = document.getElementById('result-card');
  const sentimentBadge = document.getElementById('sentiment-badge');
  const meterFill = document.getElementById('meter-fill');
  const polarityScore = document.getElementById('polarity-score');
  const wordCount = document.getElementById('word-count');
  const readTime = document.getElementById('read-time');
  const processedBy = document.getElementById('processed-by');
  const keywordsList = document.getElementById('keywords-list');

  // Load Balancer Benchmark Elements
  const testLbBtn = document.getElementById('test-lb-btn');
  const lbTableBody = document.querySelector('#lb-table tbody');

  // Task Elements
  const taskForm = document.getElementById('task-form');
  const taskTitle = document.getElementById('task-title');
  const taskPriority = document.getElementById('task-priority');
  const tasksContainer = document.getElementById('tasks-container');

  // Preset buttons
  document.querySelectorAll('.tag-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      textInput.value = btn.getAttribute('data-text');
      triggerAnalyze();
    });
  });

  // Fetch initial telemetry and start polling
  updateTelemetry();
  setInterval(updateTelemetry, 4000);
  fetchTasks();

  async function updateTelemetry() {
    try {
      const [healthRes, metricsRes] = await Promise.all([
        fetch('/health'),
        fetch('/metrics')
      ]);

      if (healthRes.ok) {
        const health = await healthRes.json();
        nodePill.textContent = health.instance_id;
        envPill.textContent = health.environment.toUpperCase();
        statMemory.textContent = `${health.memory_usage_mb} MB`;
      }

      if (metricsRes.ok) {
        const metrics = await metricsRes.json();
        statRequests.textContent = metrics.total_requests;
        statLatency.textContent = `${metrics.avg_latency_ms} ms`;
        statTasks.textContent = metrics.total_tasks;
      }
    } catch (err) {
      console.warn('Telemetry update error:', err);
    }
  }

  // Analyze text
  async function triggerAnalyze() {
    const text = textInput.value.trim();
    if (!text) return;

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = 'Analyzing...';

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (!response.ok) throw new Error('Analysis failed');

      const data = await response.json();

      // Update UI
      sentimentBadge.textContent = data.sentiment_label;
      sentimentBadge.className = 'sentiment-badge ' + 
        (data.sentiment_label === 'POSITIVE' ? 'sentiment-positive' : 
         data.sentiment_label === 'NEGATIVE' ? 'sentiment-negative' : 'sentiment-neutral');

      // Polarity score (-1 to 1) mapped to 0% to 100%
      const percentage = Math.max(0, Math.min(100, ((data.polarity_score + 1) / 2) * 100));
      meterFill.style.width = `${percentage}%`;
      meterFill.style.background = data.sentiment_label === 'POSITIVE' ? '#10b981' : 
                                   data.sentiment_label === 'NEGATIVE' ? '#ef4444' : '#6366f1';

      polarityScore.textContent = data.polarity_score;
      wordCount.textContent = data.word_count;
      readTime.textContent = `${data.estimated_read_time_seconds}s`;
      processedBy.textContent = data.processed_by_instance;

      if (data.keywords && data.keywords.length > 0) {
        keywordsList.innerHTML = data.keywords
          .map(k => `<span class="tag-btn">${k.word} (${k.count})</span>`)
          .join(' ');
      } else {
        keywordsList.innerHTML = '<span style="color:#94a3b8">None detected</span>';
      }

      resultCard.style.display = 'block';
      updateTelemetry();
    } catch (err) {
      alert('Error analyzing text: ' + err.message);
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '⚡ Analyze Sentiment & Text';
    }
  }

  analyzeBtn.addEventListener('click', triggerAnalyze);

  // Load Balancer Distribution Test
  testLbBtn.addEventListener('click', async () => {
    testLbBtn.disabled = true;
    testLbBtn.innerHTML = 'Testing Distribution...';
    lbTableBody.innerHTML = '';

    const iterations = 8;
    for (let i = 1; i <= iterations; i++) {
      const t0 = performance.now();
      try {
        const res = await fetch('/health?cb=' + Math.random());
        const t1 = performance.now();
        const instanceId = res.headers.get('X-Instance-ID') || 'Unknown Node';
        const serverLatency = res.headers.get('X-Response-Time-Ms') || '0.00';
        const totalRtt = (t1 - t0).toFixed(2);

        const row = document.createElement('tr');
        row.innerHTML = `
          <td><strong>#${i}</strong></td>
          <td><span style="font-family:monospace; color:#06b6d4;">${instanceId}</span></td>
          <td><span style="color:#10b981;">200 OK</span></td>
          <td>${serverLatency} ms</td>
          <td>${totalRtt} ms</td>
        `;
        lbTableBody.appendChild(row);
      } catch (e) {
        const row = document.createElement('tr');
        row.innerHTML = `<td>#${i}</td><td colspan="4" style="color:#ef4444;">Request Failed</td>`;
        lbTableBody.appendChild(row);
      }
    }

    testLbBtn.disabled = false;
    testLbBtn.innerHTML = '🚀 Send 8 Requests Across Nodes';
    updateTelemetry();
  });

  // Task Queue Management
  async function fetchTasks() {
    try {
      const res = await fetch('/api/tasks');
      if (res.ok) {
        const tasks = await res.json();
        renderTasks(tasks);
      }
    } catch (err) {
      console.warn('Could not fetch tasks:', err);
    }
  }

  function renderTasks(tasks) {
    if (!tasks || tasks.length === 0) {
      tasksContainer.innerHTML = '<div style="color:var(--text-muted); font-size:0.85rem; padding:0.5rem;">No tasks queued. Create one above!</div>';
      return;
    }

    tasksContainer.innerHTML = tasks.map(t => `
      <div class="task-item">
        <div>
          <div class="task-title">${escapeHtml(t.title)}</div>
          <div style="font-size:0.75rem; color:var(--text-muted); font-family:monospace;">
            ID: ${t.id} | Node: ${t.processed_by}
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
          <span class="task-badge priority-${t.priority}">${t.priority}</span>
          <button class="btn-secondary" style="padding:0.2rem 0.5rem;" onclick="deleteTaskItem('${t.id}')">✕</button>
        </div>
      </div>
    `).join('');
  }

  window.deleteTaskItem = async (taskId) => {
    try {
      await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
      fetchTasks();
      updateTelemetry();
    } catch (err) {
      console.error(err);
    }
  };

  taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = taskTitle.value.trim();
    const priority = taskPriority.value;
    if (!title) return;

    try {
      const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority, description: 'Created via CloudPulse UI' })
      });
      if (res.ok) {
        taskTitle.value = '';
        fetchTasks();
        updateTelemetry();
      }
    } catch (err) {
      alert('Failed to submit task: ' + err.message);
    }
  });

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
});
