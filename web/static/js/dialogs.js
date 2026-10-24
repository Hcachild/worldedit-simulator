const dialog = document.querySelector('#modal');

function buildField(field) {
  const label = document.createElement('label');
  label.textContent = field.label;
  const input = document.createElement('input');
  input.name = field.name;
  input.type = field.type || 'text';
  input.value = field.value ?? '';
  input.placeholder = field.placeholder || '';
  input.required = field.required !== false;
  if (field.min !== undefined) input.min = field.min;
  if (field.max !== undefined) input.max = field.max;
  if (field.step !== undefined) input.step = field.step;
  label.append(input);
  return label;
}

export function openForm({
  title,
  description = '',
  fields = [],
  submitText = '确定',
  danger = false,
  onSubmit,
}) {
  return new Promise((resolve) => {
    let settled = false;
    const finish = (value) => {
      if (settled) return;
      settled = true;
      dialog.onclose = null;
      dialog.close();
      resolve(value);
    };

    dialog.innerHTML = '';
    const form = document.createElement('form');
    form.className = 'dialog-form';

    const heading = document.createElement('h3');
    heading.textContent = title;

    const desc = document.createElement('p');
    desc.className = 'dialog-desc';
    desc.textContent = description;

    const fieldsBox = document.createElement('div');
    fieldsBox.className = 'dialog-fields';
    let row = null;
    for (const field of fields) {
      if (field.type === 'checkbox') {
        const label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.name = field.name;
        input.checked = Boolean(field.value);
        label.append(input, ` ${field.label}`);
        fieldsBox.append(label);
        row = null;
      } else if (field.inline) {
        if (!row) {
          row = document.createElement('div');
          row.className = 'dialog-row';
          fieldsBox.append(row);
        }
        row.append(buildField(field));
      } else {
        row = null;
        fieldsBox.append(buildField(field));
      }
    }

    const error = document.createElement('p');
    error.className = 'dialog-error';

    const actions = document.createElement('div');
    actions.className = 'dialog-actions';
    const cancel = document.createElement('button');
    cancel.type = 'button';
    cancel.className = 'ghost';
    cancel.textContent = '取消';
    cancel.addEventListener('click', () => finish(false));
    const submit = document.createElement('button');
    submit.type = 'submit';
    submit.className = danger ? 'danger' : 'primary';
    submit.textContent = submitText;
    actions.append(cancel, submit);

    form.append(heading, desc, fieldsBox, error, actions);
    dialog.append(form);

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const values = {};
      for (const field of fields) {
        const input = Array.from(form.elements).find((element) => element.name === field.name);
        if (!input) {
          error.textContent = `缺少字段 ${field.name}`;
          return;
        }
        values[field.name] = field.type === 'checkbox' ? input.checked : input.value.trim();
      }
      submit.disabled = true;
      error.textContent = '';
      try {
        await onSubmit(values);
        finish(true);
      } catch (exc) {
        error.textContent = exc.message || String(exc);
        submit.disabled = false;
      }
    });

    dialog.onclose = () => finish(false);
    dialog.showModal();
    const first = form.querySelector('input, select, textarea');
    if (first) first.focus();
  });
}

export function openConfirm({ title, message, confirmText = '确定', danger = false }) {
  return openForm({
    title,
    description: message,
    fields: [],
    submitText: confirmText,
    danger,
    onSubmit: async () => {},
  });
}
