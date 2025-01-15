document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signup-form');
    const signinForm = document.getElementById('signin-form');
    const viewProfileButtons = document.querySelectorAll('.view-profile');
    const sendDateRequestButtons = document.querySelectorAll('.send-date-request');
    const dateRequestForm = document.getElementById('dateRequestForm');
    const acceptRequestButtons = document.querySelectorAll('.accept-request');
    const denyRequestButtons = document.querySelectorAll('.deny-request');
    const changeRequestButtons = document.querySelectorAll('.change-request');
    const changeRequestForm = document.getElementById('changeRequestForm');
    const cancelRequestButtons = document.querySelectorAll('.cancel-request');
    const acceptAlteredRequestButtons = document.querySelectorAll('.accept-altered-request');
    const alterRequestButtons = document.querySelectorAll('.alter-request');
    const alterRequestForm = document.getElementById('alterRequestForm');

    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(signupForm);
            fetch('/signup', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert(data.message);
                    window.location.href = '/signin';
                }
            });
        });
    }

    if (signinForm) {
        signinForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(signinForm);
            fetch('/signin', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert(data.message);
                    window.location.href = '/';
                }
            });
        });
    }

    // Add this function to handle blind date profile viewing
    function loadBlindDateProfile(userId) {
        fetch(`/profile/${userId}`)
            .then(response => response.json())
            .then(data => {
                const modalBody = document.getElementById('userProfileModalBody');
                modalBody.innerHTML = `
                    <p><strong>Branch:</strong> ${data.branch}</p>
                    <p><strong>Year:</strong> ${data.year}</p>
                    <p><strong>Hobbies:</strong> ${data.hobbies}</p>
                    <p><strong>Bio:</strong> ${data.bio}</p>
                    <p><strong>Previous Relationships:</strong> ${data.previous_relationships}</p>
                    <p><strong>Previous Dates:</strong> ${data.previous_dates}</p>
                `;
                const modal = new bootstrap.Modal(document.getElementById('userProfileModal'));
                modal.show();
            });
    }

    if (viewProfileButtons) {
        viewProfileButtons.forEach(button => {
            button.addEventListener('click', function() {
                const userId = this.getAttribute('data-user-id');
                if (window.location.pathname === '/blind_dates') {
                    loadBlindDateProfile(userId);
                } else {
                    // Existing code for regular profile viewing
                    fetch(`/profile/${userId}`)
                        .then(response => response.json())
                        .then(data => {
                            const modalBody = document.getElementById('userProfileModalBody');
                            modalBody.innerHTML = `
                            <div class="text-center mb-3">
                                <img src="${data.image ? '/static/uploads/' + data.image : 'https://via.placeholder.com/150'}" alt="${data.name}" class="img-fluid rounded-circle" style="max-width: 150px;">
                            </div>
                            <p><strong>Name:</strong> ${data.name}</p>
                            <p><strong>Gender:</strong> ${data.gender}</p>
                            <p><strong>Branch:</strong> ${data.branch}</p>
                            <p><strong>Year:</strong> ${data.year}</p>
                            <p><strong>Hobbies:</strong> ${data.hobbies}</p>
                            <p><strong>Bio:</strong> ${data.bio}</p>
                            <p><strong>Previous Relationships:</strong> ${data.previous_relationships}</p>
                            <p><strong>Previous Dates:</strong> ${data.previous_dates}</p>
                        `;
                            const modal = new bootstrap.Modal(document.getElementById('userProfileModal'));
                            modal.show();
                        });
                }
            });
        });
    }

    if (sendDateRequestButtons) {
        sendDateRequestButtons.forEach(button => {
            button.addEventListener('click', function() {
                const userId = this.getAttribute('data-user-id');
                document.getElementById('receiverId').value = userId;
                const modal = new bootstrap.Modal(document.getElementById('dateRequestModal'));
                modal.show();
            });
        });
    }

    if (dateRequestForm) {
        dateRequestForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(dateRequestForm);
            const data = {
                receiver_id: formData.get('receiverId'),
                date: formData.get('date'),
                time: formData.get('time'),
                place: formData.get('place')
            };
            fetch('/send_date_request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                alert(data.message);
                const modal = bootstrap.Modal.getInstance(document.getElementById('dateRequestModal'));
                modal.hide();
                location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while sending the date request: ' + (error.error || 'Unknown error'));
            });
        });
    }

    if (acceptRequestButtons) {
        acceptRequestButtons.forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.getAttribute('data-request-id');
                respondToDateRequest(requestId, 'accept');
            });
        });
    }

    if (denyRequestButtons) {
        denyRequestButtons.forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.getAttribute('data-request-id');
                respondToDateRequest(requestId, 'deny');
            });
        });
    }

    if (changeRequestButtons) {
        changeRequestButtons.forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.getAttribute('data-request-id');
                document.getElementById('requestId').value = requestId;
                const modal = new bootstrap.Modal(document.getElementById('changeRequestModal'));
                modal.show();
            });
        });
    }

    if (changeRequestForm) {
        changeRequestForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(changeRequestForm);
            const data = Object.fromEntries(formData.entries());
            respondToDateRequest(data.requestId, 'change', data);
        });
    }

    if (cancelRequestButtons) {
        cancelRequestButtons.forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.getAttribute('data-request-id');
                if (confirm('Are you sure you want to cancel this date request?')) {
                    respondToDateRequest(requestId, 'cancel');
                }
            });
        });
    }

    if (acceptAlteredRequestButtons) {
        acceptAlteredRequestButtons.forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.getAttribute('data-request-id');
                respondToDateRequest(requestId, 'accept');
            });
        });
    }

    if (alterRequestButtons) {
        alterRequestButtons.forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.getAttribute('data-request-id');
                document.getElementById('requestId').value = requestId;
                const modal = new bootstrap.Modal(document.getElementById('alterRequestModal'));
                modal.show();
            });
        });
    }

    if (alterRequestForm) {
        alterRequestForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(alterRequestForm);
            const data = Object.fromEntries(formData.entries());
            respondToDateRequest(data.requestId, 'alter', data);
        });
    }

    function respondToDateRequest(requestId, response, newData = null) {
        const data = {
            request_id: requestId,
            response: response
        };

        if (newData) {
            data.new_date = newData.newDate;
            data.new_time = newData.newTime;
            data.new_place = newData.newPlace;
        }

        fetch('/respond_to_date_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
            if (response === 'change' || response === 'alter') {
                const modalId = response === 'change' ? 'changeRequestModal' : 'alterRequestModal';
                const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                modal.hide();
            }
            location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while responding to the date request: ' + (error.error || 'Unknown error'));
        });
    }

    const imageUploadForm = document.getElementById('image-upload-form');

    if (imageUploadForm) {
        imageUploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(imageUploadForm);
            fetch('/upload_image', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                alert(data.message);
                location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while uploading the image: ' + (error.error || 'Unknown error'));
            });
        });
    }

    function loadUserDates() {
        const userDatesContainer = document.getElementById('userDates');
        if (userDatesContainer) {
            fetch('/user_dates')
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err; });
                    }
                    return response.json();
                })
                .then(dates => {
                    userDatesContainer.innerHTML = '';
                    dates.forEach(date => {
                        const card = document.createElement('div');
                        card.className = 'col-md-4 mb-3';
                        card.innerHTML = `
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">${date.is_sender ? 'Date with' : 'Date request from'} ${date.other_user}</h5>
                                    <p class="card-text"><strong>Date:</strong> ${date.date}</p>
                                    <p class="card-text"><strong>Time:</strong> ${date.time}</p>
                                    <p class="card-text"><strong>Place:</strong> ${date.place}</p>
                                    <p class="card-text"><strong>Status:</strong> ${date.status}</p>
                                </div>
                            </div>
                        `;
                        userDatesContainer.appendChild(card);
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    userDatesContainer.innerHTML = '<p>Error loading dates: ' + (error.error || 'Unknown error') + '</p>';
                });
        }
    }

    // Call loadUserDates when the profile page loads
    if (document.getElementById('userDates')) {
        loadUserDates();
    }
});

