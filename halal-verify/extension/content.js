(() => {
  const selectors = [
    '#productTitle',
    'h1[data-automation-id="product-title"]',
    'h1',
    '[data-testid="product-title"]',
  ];

  for (const selector of selectors) {
    const node = document.querySelector(selector);
    if (node && node.textContent && node.textContent.trim()) {
      window.__halalVerifyProductName = node.textContent.trim();
      break;
    }
  }
})();
