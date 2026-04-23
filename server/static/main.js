const socket = io();
const clientGrid = document.getElementById('client-grid');
const cardTemplate = document.getElementById('client-card-template');
const channelTemplate = document.getElementById('channel-item-template');

let clients = {};

async function fetchClients() {
    const res = await fetch('/api/clients');
    const data = await res.json();
    updateUI(data);
}

function updateUI(clientData) {
    // Clear and rebuild or update existing? Let's update existing to avoid flicker
    for (const [id, client] of Object.entries(clientData)) {
        let card = document.querySelector(`.client-card[data-id="${id}"]`);
        if (!card) {
            card = createCard(id, client);
            clientGrid.appendChild(card);
        }
        updateCard(card, client);
    }
}

function createCard(id, client) {
    const clone = cardTemplate.content.cloneNode(true);
    const card = clone.querySelector('.client-card');
    card.setAttribute('data-id', id);
    return card;
}

function updateCard(card, client) {
    card.querySelector('.client-name').textContent = client.name;
    const badge = card.querySelector('.status-badge');
    badge.textContent = client.status;
    badge.className = `status-badge status-${client.status}`;

    const list = card.querySelector('.channel-list');
    // For simplicity, we'll re-render channels if the count changes or on first load
    if (Object.keys(client.channels).length > 0 && list.children.length === 0) {
        for (const [chNum, mediaId] of Object.entries(client.channels)) {
            const chClone = channelTemplate.content.cloneNode(true);
            const chItem = chClone.querySelector('.channel-item');
            chItem.setAttribute('data-channel', chNum);
            chItem.querySelector('.ch-num').textContent = chNum;
            chItem.querySelector('.media-name').textContent = client.channel_media_names[chNum] || "No Media";
            
            // Setup controls
            const id = card.getAttribute('data-id');
            chItem.querySelector('.btn-play').onclick = () => sendControl(id, 'play', chNum);
            chItem.querySelector('.btn-pause').onclick = () => sendControl(id, 'pause', chNum);
            chItem.querySelector('.btn-restart').onclick = () => sendControl(id, 'restart', chNum);
            
            const slider = chItem.querySelector('.volume-slider');
            slider.value = client.volumes[chNum] || 100;
            slider.oninput = (e) => sendVolume(id, chNum, e.target.value);
            
            // Setup initial highlights
            if (client.status_data && client.status_data.channels && client.status_data.channels[chNum]) {
                const isPlaying = client.status_data.channels[chNum].playing;
                chItem.classList.add(isPlaying ? 'is-playing' : 'is-paused');
            }

            list.appendChild(chItem);
        }
    }
}

function sendControl(clientId, action, channel) {
    socket.emit('control_playback', { client_id: clientId, action, channel });
}

function sendVolume(clientId, channel, level) {
    socket.emit('set_volume', { client_id: clientId, channel, level: parseInt(level) });
}

// Socket Events
socket.on('ui_update', (data) => {
    // data: {client_id, status, channels: {1: {playing, volume, time}, ...}}
    let card = document.querySelector(`.client-card[data-id="${data.client_id}"]`);
    if (card) {
        // Status Badge update
        if (data.status) {
            const badge = card.querySelector('.status-badge');
            badge.textContent = data.status;
            badge.className = `status-badge status-${data.status}`;
        }

        // Update individual channels
        if (data.channels) {
            Object.entries(data.channels).forEach(([chNum, chStatus]) => {
                const chItem = card.querySelector(`.channel-item[data-channel="${chNum}"]`);
                if (chItem) {
                    // Update playing state class
                    if (chStatus.playing) {
                        chItem.classList.add('is-playing');
                        chItem.classList.remove('is-paused');
                    } else {
                        chItem.classList.add('is-paused');
                        chItem.classList.remove('is-playing');
                    }

                    // Sync volume slider if not being touched
                    const slider = chItem.querySelector('.volume-slider');
                    if (!slider.matches(':active')) {
                        slider.value = chStatus.volume;
                    }

                    // Update time
                    if (chStatus.time !== undefined && chStatus.duration !== undefined) {
                        const timeStr = formatTime(chStatus.time);
                        const durationStr = formatTime(chStatus.duration);
                        chItem.querySelector('.media-time').textContent = `${timeStr} / ${durationStr}`;
                    }
                }
            });
        }

        // Update media names if provided
        if (data.channel_media_names) {
            Object.entries(data.channel_media_names).forEach(([chNum, name]) => {
                const chItem = card.querySelector(`.channel-item[data-channel="${chNum}"]`);
                if (chItem) {
                    chItem.querySelector('.media-name').textContent = name;
                }
            });
        }
    } else {
        fetchClients(); // New client appeared
    }
});

function formatTime(ms) {
    if (ms < 0) return "00:00";
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

fetchClients();
setInterval(fetchClients, 5000); // Polling as fallback for new clients
