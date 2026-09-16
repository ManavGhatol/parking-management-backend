const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Navigation Logic
document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Update active nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Show target section
            const targetId = item.getAttribute('data-target');
            sections.forEach(section => {
                if (section.id === targetId) {
                    section.classList.add('active');
                    // Fetch data if dashboard is opened
                    if (targetId === 'dashboard') {
                        fetchSlots();
                    } else if (targetId === 'database') {
                        fetchVehicles();
                    } else if (targetId === 'manage-slots') {
                        fetchManageSlots();
                    }
                } else {
                    section.classList.remove('active');
                }
            });
        });
    });

    // Initial Data Fetch
    fetchSlots();

    // Event Listeners for Forms
    document.getElementById('entry-form').addEventListener('submit', handleVehicleEntry);
    document.getElementById('exit-form').addEventListener('submit', handleVehicleExitAndPayment);
});

// Toast Notification System
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    
    // Set icon based on type
    const icon = type === 'success' ? '<i class="fa-solid fa-circle-check"></i>' : '<i class="fa-solid fa-circle-exclamation"></i>';
    
    toast.innerHTML = `${icon} ${message}`;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// Fetch Slots from Backend
async function fetchSlots() {
    const container = document.getElementById('slots-container');
    container.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading slots...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/slots/`);
        if (!response.ok) throw new Error('Failed to fetch slots');
        
        const slots = await response.json();
        
        // Update stats
        const availableSlots = slots.filter(s => s.is_available).length;
        document.getElementById('available-slots-count').textContent = availableSlots;
        document.getElementById('active-vehicles-count').textContent = slots.length - availableSlots;

        // Render slots
        container.innerHTML = '';
        if (slots.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted); grid-column: 1/-1;">No parking slots configured yet.</p>';
            return;
        }

        slots.forEach(slot => {
            const statusClass = slot.is_available ? 'available' : 'occupied';
            const statusText = slot.is_available ? 'Available' : 'Occupied';
            
            const slotEl = document.createElement('div');
            slotEl.className = `slot-item ${statusClass}`;
            slotEl.innerHTML = `
                <div class="status">${statusText}</div>
                <h4>${slot.slot_number}</h4>
                <div style="font-size: 0.75rem; color: var(--text-muted);">
                    <i class="fa-solid fa-layer-group"></i> Flr ${slot.floor_number}
                </div>
            `;
            container.appendChild(slotEl);
        });

    } catch (error) {
        console.error('Error fetching slots:', error);
        container.innerHTML = '<div style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i> Error loading slots. Ensure backend is running.</div>';
        showToast('Failed to connect to server', 'error');
    }
}

// Handle Vehicle Entry
async function handleVehicleEntry(e) {
    e.preventDefault();
    
    const regNumber = document.getElementById('reg-number').value;
    const vehicleType = document.getElementById('vehicle-type').value;
    const color = document.getElementById('vehicle-color').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');

    try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';

        const payload = {
            registration_number: regNumber,
            vehicle_type: vehicleType,
            vehicle_color: color,
            entry_time: new Date().toLocaleString()
        };

        const response = await fetch(`${API_BASE_URL}/vehicles/entry`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to register vehicle entry');
        }

        // Show Success Result
        const resultCard = document.getElementById('entry-result');
        resultCard.innerHTML = `
            <div style="color: var(--success); margin-bottom: 0.5rem;"><i class="fa-solid fa-check-circle fa-2x"></i></div>
            <h4>Entry Successful</h4>
            <p>Please provide the ticket to the customer.</p>
            <div class="ticket-display">${data.ticket_id}</div>
            <p style="font-size: 0.875rem; color: var(--text-muted);">Slot Allocated: ID ${data.slot_id}</p>
        `;
        resultCard.classList.remove('hidden');
        
        showToast('Vehicle registered successfully!');
        e.target.reset();
        
        // Refresh dashboard data silently
        fetchSlots();

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-ticket"></i> Generate Ticket & Enter';
    }
}

// Handle Vehicle Exit and Payment
async function handleVehicleExitAndPayment(e) {
    e.preventDefault();
    
    const ticketId = document.getElementById('ticket-id').value;
    const paymentMethod = document.querySelector('input[name="payment_method"]:checked').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const resultCard = document.getElementById('exit-result');

    try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';
        resultCard.classList.add('hidden');

        // 1. Process Payment First
        const paymentResponse = await fetch(`${API_BASE_URL}/vehicles/payment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ticket_id: ticketId,
                payment_method: paymentMethod
            })
        });

        const paymentData = await paymentResponse.json();
        
        if (!paymentResponse.ok && paymentData.detail !== "Payment already completed") {
            throw new Error(paymentData.detail || 'Payment processing failed');
        }

        // 2. Process Exit
        const exitResponse = await fetch(`${API_BASE_URL}/vehicles/exit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ticket_id: ticketId
            })
        });

        const exitData = await exitResponse.json();

        if (!exitResponse.ok) {
            throw new Error(exitData.detail || 'Exit processing failed');
        }

        // Show Success Result
        resultCard.innerHTML = `
            <div style="color: var(--success); margin-bottom: 0.5rem;"><i class="fa-solid fa-check-circle fa-2x"></i></div>
            <h4>Exit Processed Successfully</h4>
            <div style="margin: 1rem 0; text-align: left; background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-muted);">Amount Paid:</span>
                    <strong>$${paymentData.amount || exitData.amount_paid}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-muted);">Duration:</span>
                    <strong>${exitData.duration_minutes} mins</strong>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-muted);">Vehicle Reg:</span>
                    <strong>${exitData.registration_number}</strong>
                </div>
            </div>
            <button type="button" class="btn btn-primary" onclick="resetExitForm()" style="width: 100%;">New Transaction</button>
        `;
        resultCard.classList.remove('hidden');
        document.getElementById('exit-form').style.display = 'none';
        
        showToast('Exit and payment successful!');
        
        // Refresh dashboard data silently
        fetchSlots();

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-check-circle"></i> Process Payment & Exit';
    }
}

function resetExitForm() {
    document.getElementById('exit-form').reset();
    document.getElementById('exit-form').style.display = 'flex';
    document.getElementById('exit-result').classList.add('hidden');
}

// Fetch All Vehicles for Database
async function fetchVehicles() {
    const tbody = document.getElementById('vehicles-tbody');
    const loading = document.getElementById('vehicles-loading');
    
    tbody.innerHTML = '';
    loading.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/vehicles/`);
        if (!response.ok) throw new Error('Failed to fetch vehicles');
        
        const vehicles = await response.json();
        
        loading.style.display = 'none';

        if (vehicles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">No vehicle records found.</td></tr>';
            return;
        }

        vehicles.forEach(vehicle => {
            const entryTime = new Date(vehicle.entry_time).toLocaleString();
            const exitTime = vehicle.exit_time ? new Date(vehicle.exit_time).toLocaleString() : '-';
            const statusClass = vehicle.payment_status === 'completed' ? 'completed' : 'pending';
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="font-family: monospace; color: var(--primary); font-weight: 600;">${vehicle.ticket_id}</td>
                <td>${vehicle.registration_number}</td>
                <td style="text-transform: capitalize;">${vehicle.vehicle_type}</td>
                <td>${entryTime}</td>
                <td>${exitTime}</td>
                <td><span class="status-badge ${statusClass}">${vehicle.payment_status}</span></td>
                <td style="text-align: right;">
                    <div class="action-buttons">
                        <button class="btn-action edit" onclick='openEditVehicleModal(${JSON.stringify(vehicle).replace(/'/g, "\\'")})' title="Edit"><i class="fa-solid fa-pen-to-square"></i></button>
                        <button class="btn-action delete" onclick="deleteVehicle(${vehicle.vehicle_id})" title="Delete"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error('Error fetching vehicles:', error);
        loading.innerHTML = '<div style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i> Error loading vehicle database.</div>';
        showToast('Failed to fetch vehicle database', 'error');
    }
}

// ====== MANAGE SLOTS & CRUD ======

// Modal Logic
let currentCrudAction = null;
let currentCrudId = null;

function closeModal() {
    document.getElementById('crud-modal').classList.add('hidden');
    document.getElementById('crud-form').reset();
}

document.getElementById('crud-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('modal-submit-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Saving...';

    try {
        if (currentCrudAction === 'add-slot') {
            await createSlot();
        } else if (currentCrudAction === 'edit-slot') {
            await updateSlot(currentCrudId);
        } else if (currentCrudAction === 'edit-vehicle') {
            await updateVehicle(currentCrudId);
        }
        closeModal();
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Save';
    }
});

// Fetch Manage Slots Table
async function fetchManageSlots() {
    const tbody = document.getElementById('manage-slots-tbody');
    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;"><div class="loading-spinner"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading slots...</div></td></tr>';

    try {
        const response = await fetch(`${API_BASE_URL}/slots/`);
        if (!response.ok) throw new Error('Failed to fetch slots');
        const slots = await response.json();
        
        tbody.innerHTML = '';
        if (slots.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">No slots found.</td></tr>';
            return;
        }

        slots.forEach(slot => {
            const statusClass = slot.is_available ? 'available' : 'occupied';
            const statusText = slot.is_available ? 'Available' : 'Occupied';
            const badgeClass = slot.is_available ? 'completed' : 'pending';
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${slot.slot_id}</td>
                <td style="font-weight: 600;">${slot.slot_number}</td>
                <td>${slot.floor_number}</td>
                <td style="text-transform: capitalize;">${slot.slot_type}</td>
                <td>$${slot.hourly_rate}/hr</td>
                <td><span class="status-badge ${badgeClass}">${statusText}</span></td>
                <td style="text-align: right;">
                    <div class="action-buttons">
                        <button class="btn-action edit" onclick='openEditSlotModal(${JSON.stringify(slot).replace(/'/g, "\\'")})' title="Edit"><i class="fa-solid fa-pen-to-square"></i></button>
                        <button class="btn-action delete" onclick="deleteSlot(${slot.slot_id})" title="Delete"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        showToast('Error loading slots data', 'error');
    }
}

// Add Slot Modal
function openAddSlotModal() {
    currentCrudAction = 'add-slot';
    document.getElementById('modal-title').textContent = 'Add New Parking Slot';
    document.getElementById('modal-body').innerHTML = `
        <div class="form-group">
            <label>Slot Number</label>
            <input type="text" id="crud-slot-number" required>
        </div>
        <div class="form-row" style="margin-top: 1rem;">
            <div class="form-group">
                <label>Floor</label>
                <input type="number" id="crud-slot-floor" value="1" required>
            </div>
            <div class="form-group">
                <label>Type</label>
                <select id="crud-slot-type">
                    <option value="regular">Regular</option>
                    <option value="handicapped">Handicapped</option>
                    <option value="compact">Compact</option>
                </select>
            </div>
        </div>
        <div class="form-row" style="margin-top: 1rem;">
            <div class="form-group">
                <label>Hourly Rate ($)</label>
                <input type="number" step="0.1" id="crud-slot-hourly" value="5.0" required>
            </div>
            <div class="form-group">
                <label>Location Area</label>
                <input type="text" id="crud-slot-location" value="Zone A">
            </div>
        </div>
    `;
    document.getElementById('crud-modal').classList.remove('hidden');
}

// Edit Slot Modal
function openEditSlotModal(slot) {
    currentCrudAction = 'edit-slot';
    currentCrudId = slot.slot_id;
    document.getElementById('modal-title').textContent = 'Edit Parking Slot';
    document.getElementById('modal-body').innerHTML = `
        <div class="form-group">
            <label>Slot Number</label>
            <input type="text" id="crud-slot-number" value="${slot.slot_number}" required>
        </div>
        <div class="form-row" style="margin-top: 1rem;">
            <div class="form-group">
                <label>Floor</label>
                <input type="number" id="crud-slot-floor" value="${slot.floor_number}" required>
            </div>
            <div class="form-group">
                <label>Type</label>
                <select id="crud-slot-type">
                    <option value="regular" ${slot.slot_type==='regular'?'selected':''}>Regular</option>
                    <option value="handicapped" ${slot.slot_type==='handicapped'?'selected':''}>Handicapped</option>
                    <option value="compact" ${slot.slot_type==='compact'?'selected':''}>Compact</option>
                </select>
            </div>
        </div>
        <div class="form-row" style="margin-top: 1rem;">
            <div class="form-group">
                <label>Hourly Rate ($)</label>
                <input type="number" step="0.1" id="crud-slot-hourly" value="${slot.hourly_rate}" required>
            </div>
            <div class="form-group">
                <label>Location Area</label>
                <input type="text" id="crud-slot-location" value="${slot.location || ''}">
            </div>
        </div>
    `;
    document.getElementById('crud-modal').classList.remove('hidden');
}

async function createSlot() {
    const payload = {
        slot_number: document.getElementById('crud-slot-number').value,
        floor_number: parseInt(document.getElementById('crud-slot-floor').value),
        slot_type: document.getElementById('crud-slot-type').value,
        hourly_rate: parseFloat(document.getElementById('crud-slot-hourly').value),
        daily_rate: parseFloat(document.getElementById('crud-slot-hourly').value) * 8, // dummy calculation
        slot_length: 5.0,
        location: document.getElementById('crud-slot-location').value
    };

    const response = await fetch(`${API_BASE_URL}/slots/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create slot');
    }
    showToast('Slot created successfully');
    fetchManageSlots();
}

async function updateSlot(id) {
    const payload = {
        slot_number: document.getElementById('crud-slot-number').value,
        floor_number: parseInt(document.getElementById('crud-slot-floor').value),
        slot_type: document.getElementById('crud-slot-type').value,
        hourly_rate: parseFloat(document.getElementById('crud-slot-hourly').value),
        daily_rate: parseFloat(document.getElementById('crud-slot-hourly').value) * 8,
        slot_length: 5.0,
        location: document.getElementById('crud-slot-location').value
    };

    const response = await fetch(`${API_BASE_URL}/slots/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update slot');
    }
    showToast('Slot updated successfully');
    fetchManageSlots();
}

async function deleteSlot(id) {
    if(!confirm('Are you sure you want to delete this parking slot?')) return;
    try {
        const response = await fetch(`${API_BASE_URL}/slots/${id}`, { method: 'DELETE' });
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to delete slot');
        }
        showToast('Slot deleted successfully');
        fetchManageSlots();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteVehicle(id) {
    if(!confirm('Are you sure you want to delete this vehicle record? This action cannot be undone.')) return;
    try {
        const response = await fetch(`${API_BASE_URL}/vehicles/${id}`, { method: 'DELETE' });
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to delete vehicle');
        }
        showToast('Vehicle deleted successfully');
        fetchVehicles();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// Edit Vehicle Modal
function openEditVehicleModal(vehicle) {
    currentCrudAction = 'edit-vehicle';
    currentCrudId = vehicle.vehicle_id;
    document.getElementById('modal-title').textContent = 'Edit Vehicle Record';
    document.getElementById('modal-body').innerHTML = `
        <div class="form-group">
            <label>Registration Number</label>
            <input type="text" id="crud-vehicle-reg" value="${vehicle.registration_number}" required>
        </div>
        <div class="form-row" style="margin-top: 1rem;">
            <div class="form-group">
                <label>Vehicle Type</label>
                <select id="crud-vehicle-type">
                    <option value="car" ${vehicle.vehicle_type==='car'?'selected':''}>Car</option>
                    <option value="bike" ${vehicle.vehicle_type==='bike'?'selected':''}>Bike</option>
                    <option value="van" ${vehicle.vehicle_type==='van'?'selected':''}>Van</option>
                    <option value="truck" ${vehicle.vehicle_type==='truck'?'selected':''}>Truck</option>
                </select>
            </div>
            <div class="form-group">
                <label>Color</label>
                <input type="text" id="crud-vehicle-color" value="${vehicle.vehicle_color || ''}">
            </div>
        </div>
    `;
    document.getElementById('crud-modal').classList.remove('hidden');
}

async function updateVehicle(id) {
    const payload = {
        registration_number: document.getElementById('crud-vehicle-reg').value,
        vehicle_type: document.getElementById('crud-vehicle-type').value,
        vehicle_color: document.getElementById('crud-vehicle-color').value
    };

    const response = await fetch(`${API_BASE_URL}/vehicles/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update vehicle');
    }
    showToast('Vehicle updated successfully');
    fetchVehicles();
}
