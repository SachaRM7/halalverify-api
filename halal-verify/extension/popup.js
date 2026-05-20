const apiBase = 'http://localhost:8000';

async function getActiveProductName() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => window.__halalVerifyProductName || document.title,
  });
  return result;
}

async function lookup() {
  const nameEl = document.getElementById('product-name');
  const statusEl = document.getElementById('status');
  const detailsEl = document.getElementById('details');
  const reportBtn = document.getElementById('report-btn');

  const productName = await getActiveProductName();
  nameEl.textContent = productName;

  const response = await fetch(`${apiBase}/v1/search?q=${encodeURIComponent(productName)}&page_size=1`);
  if (!response.ok) {
    detailsEl.textContent = 'API unavailable';
    return;
  }

  const payload = await response.json();
  const item = payload.items[0];
  if (!item) {
    detailsEl.textContent = 'No halal data found yet.';
    statusEl.textContent = 'unknown';
    statusEl.className = 'badge unknown';
    return;
  }

  statusEl.textContent = item.status;
  statusEl.className = `badge ${item.status}`;
  detailsEl.textContent = `${item.type} • confidence: ${item.confidence}`;
  reportBtn.onclick = () => {
    window.open(`${apiBase}/docs`, '_blank');
  };
}

lookup().catch((error) => {
  document.getElementById('details').textContent = `Lookup failed: ${error.message}`;
});
