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
    const searchForm = document.getElementById('search-form');
    const filterForm = document.getElementById('filter-form');
    const userCards = document.getElementById('user-cards');

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
                    <p><strong>Pet Preference:</strong> ${data.pet_preference}</p>
                    <p><strong>Sleep Schedule:</strong> ${data.sleep_schedule}</p>
                    <p><strong>Life Approach:</strong> ${data.life_approach}</p>
                    <p><strong>Personality Type:</strong> ${data.personality_type}</p>
                    <p><strong>Beverage Preference:</strong> ${data.beverage_preference}</p>
                    <p><strong>Ideal Weekend:</strong> ${data.ideal_weekend}</p>
                    <p><strong>Vacation Style:</strong> ${data.vacation_style}</p>
                    <p><strong>Music Taste:</strong> ${data.music_taste}</p>
                    <p><strong>Sunday Activity:</strong> ${data.sunday_activity}</p>
                    <p><strong>Love Language:</strong> ${data.love_language}</p>
                    <p><strong>Planning Style:</strong> ${data.planning_style}</p>
                    <p><strong>Dream Date:</strong> ${data.dream_date}</p>
                    <p><strong>Living Preference:</strong> ${data.living_preference}</p>
                    <p><strong>Communication Style:</strong> ${data.communication_style}</p>
                    <p><strong>Motivation Factor:</strong> ${data.motivation_factor}</p>
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

    function updateUsers() {
        const searchQuery = document.getElementById('search-input').value;
        const filterData = new FormData(filterForm);
        const queryParams = new URLSearchParams(filterData);
        queryParams.append('search', searchQuery);

        fetch(`/api/users?${queryParams.toString()}`)
            .then(response => response.json())
            .then(users => {
                userCards.innerHTML = '';
                users.forEach(user => {
                    const userCard = createUserCard(user);
                    userCards.appendChild(userCard);
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    function createUserCard(user) {
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-4 user-card';
        card.innerHTML = `
            <div class="card">
                <div class="card-body text-center">
                    <img src="${user.image ? '/static/uploads/' + user.image : 'https://via.placeholder.com/150'}" alt="${user.name}" class="img-fluid rounded-circle mb-3" style="max-width: 100px;">
                    <h5 class="card-title">${user.name}</h5>
                    <p class="card-text"><strong>Branch:</strong> ${user.branch}</p>
                    <p class="card-text"><strong>Year:</strong> ${user.year}</p>
                    <p class="card-text"><strong>Personality:</strong> ${user.personality_type}</p>
                    <p class="card-text"><strong>Music Taste:</strong> ${user.music_taste}</p>
                    <button class="btn btn-primary view-profile" data-user-id="${user.id}">View Full Profile</button>
                    <button class="btn btn-success mt-2 send-date-request" data-user-id="${user.id}">Send Date Request</button>
                </div>
            </div>
        `;
        return card;
    }

    // Add event listeners for real-time filtering
    if (searchForm) {
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('input', updateUsers);
    }

    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('select');
        filterInputs.forEach(input => {
            input.addEventListener('change', updateUsers);
        });
    }
});

