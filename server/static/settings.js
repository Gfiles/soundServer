// We'll use socket.io for settings too to ensure real-time feedback
// However, since we need socket.io-client, we need to include it in settings.html too
// I'll add it to the html in a moment.

let clients = {};
let media = {};

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const mediaList = document.getElementById('media-list');
const clientList = document.getElementById('client-mapping-list');
const configTemplate = document.getElementById('client-config-template');

async function init() {
    await fetchData();
    renderMedia();
    renderClients();
}

async function fetchData() {
    const [cRes, mRes] = await Promise.all([
        fetch('/api/clients'),
        fetch('/api/media')
    ]);
    clients = await cRes.json();
    media = await mRes.json();
}

function renderMedia() {
    mediaList.innerHTML = '';
    Object.entries(media).forEach(([id, m]) => {
        const div = document.createElement('div');
        div.className = 'media-item';
        div.style.padding = '0.5rem';
        div.style.background = 'rgba(255,255,255,0.05)';
        div.style.borderRadius = '0.5rem';
        div.textContent = m.name;
        mediaList.appendChild(div);
    });
}

function renderClients() {
    clientList.innerHTML = '';
    Object.entries(clients).forEach(([id, c]) => {
        const clone = configTemplate.content.cloneNode(true);
        clone.querySelector('.config-client-name').textContent = c.name;
        
        const chContainer = clone.querySelector('.channel-configs');
        // Let's support 2 channels for now
        [1, 2].forEach(chNum => {
            const row = document.createElement('div');
            row.innerHTML = `<label>Channel ${chNum}</label>`;
            const select = document.createElement('select');
            select.className = `ch-select-${chNum}`;
            select.innerHTML = '<option value="">None</option>';
            Object.entries(media).forEach(([mId, m]) => {
                const opt = document.createElement('option');
                opt.value = mId;
                opt.textContent = m.name;
                if (c.channels[chNum] === mId) opt.selected = true;
                select.appendChild(opt);
            });
            row.appendChild(select);
            chContainer.appendChild(row);
        });

        clone.querySelector('.btn-save').onclick = () => {
            const ch1 = chContainer.querySelector('.ch-select-1').value;
            const ch2 = chContainer.querySelector('.ch-select-2').value;
            saveMapping(id, { 1: ch1, 2: ch2 });
        };

        clientList.appendChild(clone);
    });
}

function saveMapping(clientId, channels) {
    // We'll use a temporary socket or just the global one if we include it
    if (window.io) {
        const socket = io();
        socket.emit('update_mapping', { client_id: clientId, channels });
        alert('Configuration Sent!');
    }
}

// Upload Logic
dropZone.onclick = () => fileInput.click();
fileInput.onchange = () => handleFiles(fileInput.files);
dropZone.ondragover = (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--accent)'; };
dropZone.ondragleave = () => { dropZone.style.borderColor = 'var(--glass-border)'; };
dropZone.ondrop = (e) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
};

async function handleFiles(files) {
    for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        await fetch('/api/media', { method: 'POST', body: formData });
    }
    await fetchData();
    renderMedia();
    renderClients();
}

init();
