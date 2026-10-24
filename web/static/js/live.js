export class LiveSync {
  constructor({ onEvent }) {
    this.onEvent = onEvent;
    this.source = null;
    this.lastRevision = -1;
    this.openedOnce = false;
  }

  noteRevision(revision) {
    if (Number.isFinite(revision) && revision > this.lastRevision) {
      this.lastRevision = revision;
    }
  }

  start() {
    if (this.source) return;
    this.source = new EventSource('/api/events');
    this.source.onopen = () => {
      if (this.openedOnce) this.lastRevision = -1;
      this.openedOnce = true;
    };
    this.source.onmessage = (event) => {
      let data;
      try {
        data = JSON.parse(event.data);
      } catch {
        return;
      }
      if (!Number.isFinite(data.revision) || data.revision <= this.lastRevision) return;
      this.lastRevision = data.revision;
      this.onEvent(data);
    };
  }

  stop() {
    if (this.source) {
      this.source.close();
      this.source = null;
    }
  }
}
