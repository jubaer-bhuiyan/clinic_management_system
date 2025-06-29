//
Record
Management
Functions

function editRecord(recordId) {
    fetch(`/get-record-details/${recordId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Fill the form with existing data
            const form = document.getElementById('recordForm');
            form.patient.value = data.patient_id;
            form.category.value = data.category;
            form.diagnosis.value = data.diagnosis;
            form.prescription.value = data.prescription;
            form.notes.value = data.notes || '';
            form.status.value = data.status;
            
            // Update modal title and save button
            document.getElementById('recordModalLabel').textContent = 'Edit Medical Record';
            const saveButton = document.querySelector('#recordModal .btn-primary');
            saveButton.textContent = 'Update Record';
            saveButton.onclick = () => updateRecord(recordId);
            
            // Show the modal
            $('#recordModal').modal('show');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while fetching record details: ' + error.message);
        });
}

function updateRecord(recordId) {
    const form = document.getElementById('recordForm');
    const formData = {
        category: form.category.value,
        diagnosis: form.diagnosis.value,
        prescription: form.prescription.value,
        notes: form.notes.value,
        status: form.status.value
    };
    
    fetch(`/update-record/${recordId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            $('#recordModal').modal('hide');
            location.reload();
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the record: ' + error.message);
    });
}

function viewRecord(recordId) {
    currentRecordId = recordId;
    fetch(`/get-record-details/${recordId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            const content = `
                <div class="record-details">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <p><strong>Patient:</strong> ${data.patient_name}</p>
                            <p><strong>Doctor:</strong> ${data.doctor_name}</p>
                            <p><strong>Date:</strong> ${data.date}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Category:</strong> ${data.category}</p>
                            <p><strong>Status:</strong> ${data.status}</p>
                        </div>
                    </div>
                    <hr>
                    <div class="mb-3">
                        <h6>Diagnosis</h6>
                        <p>${data.diagnosis}</p>
                    </div>
                    <div class="mb-3">
                        <h6>Prescription</h6>
                        <p>${data.prescription}</p>
                    </div>
                    ${data.notes ? `
                        <div class="mb-3">
                            <h6>Notes</h6>
                            <p>${data.notes}</p>
                        </div>
                    ` : ''}
                </div>
            `;
            
            document.getElementById('viewRecordContent').innerHTML = content;
            $('#viewRecordModal').modal('show');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while fetching record details: ' + error.message);
        });
}

function saveRecord() {
    const form = document.getElementById('recordForm');
    const formData = {
        patient: form.patient.value,
        doctor: doctorId,
        category: form.category.value,
        diagnosis: form.diagnosis.value,
        prescription: form.prescription.value,
        notes: form.notes.value,
        status: form.status.value
    };
    
    fetch('/add-record/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            $('#recordModal').modal('hide');
            location.reload();
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving the record: ' + error.message);
    });
}

function downloadRecord(recordId) {
    if (!recordId) {
        alert('No record selected for download.');
        return;
    }
    window.location.href = `/download-record/${recordId}/`;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
