async function request(path, options = {}) {
  const response = await fetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.ok === false) {
    const error = new Error(data.error || `HTTP ${response.status}`);
    error.payload = data;
    throw error;
  }
  return data;
}

function post(path, body) {
  return request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  });
}

export const api = {
  state: () => request('/api/state'),
  files: () => request('/api/files'),
  load: (name) => post('/api/load', { name }),
  newFile: (payload) => post('/api/new', payload),
  upload: (name, buffer) => request(`/api/upload?name=${encodeURIComponent(name)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/octet-stream' },
    body: buffer,
  }),
  rename: (name, newName) => post('/api/rename', { name, newName }),
  duplicate: (name, newName) => post('/api/duplicate', { name, newName }),
  deleteFile: (name) => post('/api/delete', { name }),
  close: () => post('/api/close'),
  save: () => post('/api/save'),
  saveAs: (name, overwrite) => post('/api/save-as', { name, overwrite: Boolean(overwrite) }),
  reset: () => post('/api/reset'),
  reveal: () => post('/api/reveal'),
  async runRaw(commands) {
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ commands }),
    });
    return response.json().catch(() => ({ ok: false, error: `HTTP ${response.status}` }));
  },
  downloadUrl: (name) => (name ? `/api/download?name=${encodeURIComponent(name)}` : '/api/download'),
};
