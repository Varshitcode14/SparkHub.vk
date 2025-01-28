document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signup-form")
  const signinForm = document.getElementById("signin-form")
  const viewProfileButtons = document.querySelectorAll(".view-profile")
  const sendDateRequestButtons = document.querySelectorAll(".send-date-request")
  const dateRequestForm = document.getElementById("dateRequestForm")
  const acceptRequestButtons = document.querySelectorAll(".accept-request")
  const denyRequestButtons = document.querySelectorAll(".deny-request")
  const changeRequestButtons = document.querySelectorAll(".change-request")
  const changeRequestForm = document.getElementById("changeRequestForm")
  const cancelRequestButtons = document.querySelectorAll(".cancel-request")
  const acceptAlteredRequestButtons = document.querySelectorAll(".accept-altered-request")
  const alterRequestButtons = document.querySelectorAll(".alter-request")
  const alterRequestForm = document.getElementById("alterRequestForm")
  const searchForm = document.getElementById("search-form")
  const filterForm = document.getElementById("filter-form")
  const userCards = document.getElementById("user-cards")
  const searchInput = document.getElementById("search-input")
  const togglePasswordButtons = document.querySelectorAll(".toggle-password")

  if (togglePasswordButtons) {
    togglePasswordButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const targetId = this.getAttribute("data-target")
        const passwordInput = document.getElementById(targetId)
        const icon = this.querySelector("i")

        if (passwordInput.type === "password") {
          passwordInput.type = "text"
          icon.classList.remove("bi-eye")
          icon.classList.add("bi-eye-slash")
        } else {
          passwordInput.type = "password"
          icon.classList.remove("bi-eye-slash")
          icon.classList.add("bi-eye")
        }
      })
    })
  }

  if (signupForm) {
    const password = document.getElementById("password")
    const confirmPassword = document.getElementById("confirm-password")
    const passwordMismatchMessage = document.getElementById("password-mismatch-message")
    const acceptTermsCheckbox = document.getElementById("acceptTerms")

    function validatePassword() {
      if (password.value !== confirmPassword.value) {
        passwordMismatchMessage.style.display = "block"
        confirmPassword.setCustomValidity("Passwords do not match")
      } else {
        passwordMismatchMessage.style.display = "none"
        confirmPassword.setCustomValidity("")
      }
    }

    password.addEventListener("change", validatePassword)
    confirmPassword.addEventListener("keyup", validatePassword)

    signupForm.addEventListener("submit", (e) => {
      e.preventDefault()
      validatePassword()

      if (!acceptTermsCheckbox.checked) {
        alert("You must accept the Terms and Conditions to sign up.")
        return
      }

      if (signupForm.checkValidity()) {
        const formData = new FormData(signupForm)

        const favoriteSports = Array.from(formData.getAll("favorite_sports")).join(",")
        formData.set("favorite_sports", favoriteSports)

        // Update the societies handling to exclude 'None' if other options are selected
        const selectedSocieties = Array.from(formData.getAll("societies")).filter((society) => society !== "None")
        formData.set("societies", selectedSocieties.length > 0 ? selectedSocieties.join(",") : "None")

        fetch("/signup", {
          method: "POST",
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.error) {
              alert(data.error)
            } else {
              alert(data.message)
              window.location.href = "/signin"
            }
          })
      } else {
        signupForm.classList.add("was-validated")
      }
    })
  }

  if (signinForm) {
    signinForm.addEventListener("submit", (e) => {
      e.preventDefault()
      const formData = new FormData(signinForm)
      fetch("/signin", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            alert(data.error)
          } else {
            alert(data.message)
            window.location.href = "/"
          }
        })
    })
  }

  function loadUserProfile(userId, isBlind) {
    const url = isBlind ? `/blind_profile/${userId}` : `/profile/${userId}`
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        const modalBody = document.getElementById("userProfileModalBody")
        const modalTitle = document.getElementById("userProfileModalLabel")

        if (isBlind) {
          modalTitle.textContent = "Mystery User Profile"
          modalBody.innerHTML = `
            <div class="profile-info">
              <p><strong>Branch:</strong> ${data.branch}</p>
              <p><strong>Year:</strong> ${data.year}</p>
              <p><strong>State:</strong> ${data.state || "Not specified"}</p>
              <p><strong>Hobbies:</strong> ${data.hobbies || "Not specified"}</p>
              <p><strong>Bio:</strong> ${data.bio || "Not specified"}</p>
              <p><strong>Ideal Weekend:</strong> ${data.ideal_weekend || "Not specified"}</p>
              <p><strong>Music Taste:</strong> ${data.music_taste || "Not specified"}</p>
              <p><strong>Dream Date:</strong> ${data.dream_date || "Not specified"}</p>
              <p><strong>Favorite Sports:</strong> ${data.favorite_sports || "Not specified"}</p>
              <p><strong>Societies:</strong> ${data.societies || "Not specified"}</p>
              <p><strong>Leisure Activities:</strong> ${data.leisure_activities || "Not specified"}</p>
              <p><strong>Sleep Schedule:</strong> ${data.sleep_schedule ? data.sleep_schedule.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase()) : "Not specified"}</p>
              <p><strong>Aspirations:</strong> ${data.aspirations ? data.aspirations.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase()) : "Not specified"}</p>
              <p><strong>Personality Type:</strong> ${data.personality_type ? data.personality_type.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase()) : "Not specified"}</p>
              <p><strong>Communication Style:</strong> ${data.communication_style || "Not specified"}</p>
              <p><strong>Looking for:</strong> ${data.relationship_looking_for ? data.relationship_looking_for.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase()) : "Not specified"}</p>
            </div>
          `
        } else {
          modalTitle.textContent = "User Profile"
          modalBody.innerHTML = `
            <div class="text-center mb-3">
              <img src="${data.image ? "/static/uploads/" + data.image : "https://via.placeholder.com/150"}" alt="${data.name}" class="img-fluid rounded-circle" style="max-width: 150px;">
            </div>
            <p><strong>Name:</strong> ${data.name}</p>
            <p><strong>Email:</strong> ${data.email}</p>
            <p><strong>Gender:</strong> ${data.gender}</p>
            <p><strong>Branch:</strong> ${data.branch}</p>
            <p><strong>Year:</strong> ${data.year}</p>
            <p><strong>State:</strong> ${data.state || "Not specified"}</p>
            <p><strong>Hobbies:</strong> ${data.hobbies}</p>
            <p><strong>Bio:</strong> ${data.bio}</p>
            <p><strong>Instagram ID:</strong> ${data.insta_id}</p>
            <p><strong>Ideal Weekend:</strong> ${data.ideal_weekend}</p>
            <p><strong>Music Taste:</strong> ${data.music_taste}</p>
            <p><strong>Dream Date:</strong> ${data.dream_date}</p>
            <p><strong>Favorite Sports:</strong> ${data.favorite_sports}</p>
            <p><strong>Societies:</strong> ${data.societies}</p>
            <p><strong>Leisure Activities:</strong> ${data.leisure_activities}</p>
            ${data.cgpa ? `<p><strong>CGPA:</strong> ${data.cgpa}</p>` : ""}
            <p><strong>Sleep Schedule:</strong> ${data.sleep_schedule ? data.sleep_schedule.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase()) : "Not specified"}</p>
            <p><strong>Aspirations:</strong> ${data.aspirations ? data.aspirations.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase()) : "Not specified"}</p>
            <p><strong>Personality Type:</strong> ${data.personality_type ? data.personality_type.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase()) : "Not specified"}</p>
            <p><strong>Communication Style:</strong> ${data.communication_style || "Not specified"}</p>
            <p><strong>Looking for:</strong> ${data.relationship_looking_for ? data.relationship_looking_for.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase()) : "Not specified"}</p>
          `
        }
        const modalElement = document.getElementById("userProfileModal")
        const modal = new bootstrap.Modal(modalElement)
        modal.show()
        modalElement.addEventListener("hidden.bs.modal", () => {
          document.body.classList.remove("modal-open")
          document.body.style.overflow = ""
          document.body.style.paddingRight = ""
          const modalBackdrop = document.querySelector(".modal-backdrop")
          if (modalBackdrop) {
            modalBackdrop.remove()
          }
        })
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("An error occurred while loading the user profile.")
      })
  }

  if (viewProfileButtons) {
    viewProfileButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const userId = this.getAttribute("data-user-id")
        const isBlind = this.getAttribute("data-is-blind") === "true"

        loadUserProfile(userId, isBlind)
      })
    })
  }

  if (sendDateRequestButtons) {
    sendDateRequestButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const userId = this.getAttribute("data-user-id")
        const isBlind = this.getAttribute("data-is-blind") === "true"
        document.getElementById("receiverId").value = userId
        document.getElementById("isBlindDate").value = isBlind
        const modal = new bootstrap.Modal(document.getElementById("dateRequestModal"))
        modal.show()
      })
    })
  }

  if (dateRequestForm) {
    dateRequestForm.addEventListener("submit", (e) => {
      e.preventDefault()
      const formData = new FormData(dateRequestForm)
      const data = {
        receiver_id: formData.get("receiverId"),
        date: formData.get("date"),
        time: formData.get("time"),
        place: formData.get("place"),
        is_blind_date: formData.get("isBlindDate") === "true",
      }
      fetch("/send_date_request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((err) => {
              throw err
            })
          }
          return response.json()
        })
        .then((data) => {
          alert(data.message)
          const modalElement = document.getElementById("dateRequestModal")
          const modalInstance = bootstrap.Modal.getInstance(modalElement)
          if (modalInstance) {
            modalInstance.hide()
          }
          location.reload()
        })
        .catch((error) => {
          console.error("Error:", error)
          alert("An error occurred while sending the date request: " + (error.error || "Unknown error"))
        })
    })
  }

  if (acceptRequestButtons) {
    acceptRequestButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const requestId = this.getAttribute("data-request-id")
        respondToDateRequest(requestId, "accept")
      })
    })
  }

  if (denyRequestButtons) {
    denyRequestButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const requestId = this.getAttribute("data-request-id")
        respondToDateRequest(requestId, "deny")
      })
    })
  }

  if (changeRequestButtons) {
    changeRequestButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const requestId = this.getAttribute("data-request-id")
        document.getElementById("requestId").value = requestId
        const modal = new bootstrap.Modal(document.getElementById("changeRequestModal"))
        modal.show()
      })
    })
  }

  if (changeRequestForm) {
    changeRequestForm.addEventListener("submit", (e) => {
      e.preventDefault()
      const formData = new FormData(changeRequestForm)
      const data = Object.fromEntries(formData.entries())
      respondToDateRequest(data.requestId, "change", data)
    })
  }

  if (cancelRequestButtons) {
    cancelRequestButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const requestId = this.getAttribute("data-request-id")
        if (confirm("Are you sure you want to cancel this date request?")) {
          respondToDateRequest(requestId, "cancel")
        }
      })
    })
  }

  if (acceptAlteredRequestButtons) {
    acceptAlteredRequestButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const requestId = this.getAttribute("data-request-id")
        respondToDateRequest(requestId, "accept")
      })
    })
  }

  if (alterRequestButtons) {
    alterRequestButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const requestId = this.getAttribute("data-request-id")
        document.getElementById("requestId").value = requestId
        const modal = new bootstrap.Modal(document.getElementById("alterRequestModal"))
        modal.show()
      })
    })
  }

  if (alterRequestForm) {
    alterRequestForm.addEventListener("submit", (e) => {
      e.preventDefault()
      const formData = new FormData(alterRequestForm)
      const data = Object.fromEntries(formData.entries())
      respondToDateRequest(data.requestId, "alter", data)
    })
  }

  function respondToDateRequest(requestId, response, newData = null) {
    const data = {
      request_id: requestId,
      response: response,
    }

    if (newData) {
      data.new_date = newData.newDate
      data.new_time = newData.newTime
      data.new_place = newData.newPlace
    }

    fetch("/respond_to_date_request", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((err) => {
            throw err
          })
        }
        return response.json()
      })
      .then((data) => {
        alert(data.message)
        if (response === "change" || response === "alter") {
          const modalId = response === "change" ? "changeRequestModal" : "alterRequestModal"
          const modal = bootstrap.Modal.getInstance(document.getElementById(modalId))
          modal.hide()
        }
        location.reload()
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("An error occurred while responding to the date request: " + (error.error || "Unknown error"))
      })
  }

  const imageUploadForm = document.getElementById("image-upload-form")

  if (imageUploadForm) {
    imageUploadForm.addEventListener("submit", (e) => {
      e.preventDefault()
      const formData = new FormData(imageUploadForm)
      fetch("/upload_image", {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((err) => {
              throw err
            })
          }
          return response.json()
        })
        .then((data) => {
          alert(data.message)
          location.reload()
        })
        .catch((error) => {
          console.error("Error:", error)
          alert("An error occurred while uploading the image: " + (error.error || "Unknown error"))
        })
    })
  }

  function loadUserDates() {
    const userDatesContainer = document.getElementById("userDates")
    if (userDatesContainer) {
      fetch("/user_dates")
        .then((response) => {
          if (!response.ok) {
            return response.json().then((err) => {
              throw err
            })
          }
          return response.json()
        })
        .then((dates) => {
          userDatesContainer.innerHTML = ""
          dates.forEach((date) => {
            const card = document.createElement("div")
            card.className = "col-md-4 mb-3"
            card.innerHTML = `
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">${date.is_sender ? "Date with" : "Date request from"} ${date.other_user}</h5>
                  <p class="card-text"><strong>Date:</strong> ${date.date}</p>
                  <p class="card-text"><strong>Time:</strong> ${date.time}</p>
                  <p class="card-text"><strong>Place:</strong> ${date.place}</p>
                  <p class="card-text"><strong>Status:</strong> ${date.status}</p>
                </div>
              </div>
            `
            userDatesContainer.appendChild(card)
          })
        })
        .catch((error) => {
          console.error("Error:", error)
          userDatesContainer.innerHTML = "<p>Error loading dates: " + (error.error || "Unknown error") + "</p>"
        })
    }
  }

  // Call loadUserDates when the profile page loads
  if (document.getElementById("userDates")) {
    loadUserDates()
  }

  function updateUsers() {
    const searchQuery = searchInput ? searchInput.value : ""
    const filterData = new FormData(filterForm)
    const queryParams = new URLSearchParams(filterData)
    queryParams.append("search", searchQuery)

    fetch(`/api/users?${queryParams.toString()}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok")
        }
        return response.json()
      })
      .then((users) => {
        userCards.innerHTML = ""
        users.forEach((user) => {
          const userCard = createUserCard(user)
          userCards.appendChild(userCard)
        })
        attachButtonListeners()
      })
      .catch((error) => {
        console.error("Error:", error)
        userCards.innerHTML = "<p>Error loading users. Please try again.</p>"
      })
  }

  function updateBlindDates() {
    const filterForm = document.getElementById("filter-form")
    const userCards = document.getElementById("user-cards")

    if (filterForm && userCards) {
      const formData = new FormData(filterForm)
      const queryParams = new URLSearchParams(formData)

      fetch(`/blind_dates?${queryParams.toString()}`)
        .then((response) => response.text())
        .then((html) => {
          const parser = new DOMParser()
          const doc = parser.parseFromString(html, "text/html")
          const newUserCards = doc.getElementById("user-cards")

          if (newUserCards) {
            userCards.innerHTML = newUserCards.innerHTML
            attachButtonListeners()
          }
        })
        .catch((error) => {
          console.error("Error:", error)
          userCards.innerHTML = "<p>Error loading users. Please try again.</p>"
        })
    }
  }

  function createUserCard(user) {
    const card = document.createElement("div")
    card.className = "col-md-4 mb-4 user-card"
    card.innerHTML = `
      <div class="card h-100">
        <div class="card-body text-center d-flex flex-column">
          <img src="${user.image ? "/static/uploads/" + user.image : "https://via.placeholder.com/150"}" alt="${user.name}" class="img-fluid rounded-circle mb-3 mx-auto" style="max-width: 100px;">
          <h5 class="card-title">${user.name}</h5>
          <p class="card-text"><strong>Branch:</strong> ${user.branch}</p>
          <p class="card-text"><strong>Year:</strong> ${user.year}</p>
          <p class="card-text"><strong>Personality:</strong> ${user.personality_type || "Not specified"}</p>
          <p class="card-text"><strong>Music Taste:</strong> ${user.music_taste || "Not specified"}</p>
          <div class="mt-auto">
            <button class="btn btn-primary view-profile" data-user-id="${user.id}" data-is-blind="false">View Full Profile</button>
            <button class="btn btn-success mt-2 send-date-request" data-user-id="${user.id}" data-is-blind="false">Send Date Request</button>
          </div>
        </div>
      </div>
    `
    return card
  }

  function attachButtonListeners() {
    document.querySelectorAll(".view-profile").forEach((button) => {
      button.addEventListener("click", function () {
        const userId = this.getAttribute("data-user-id")
        const isBlind = this.getAttribute("data-is-blind") === "true"
        loadUserProfile(userId, isBlind)
      })
    })

    document.querySelectorAll(".send-date-request").forEach((button) => {
      button.addEventListener("click", function () {
        const userId = this.getAttribute("data-user-id")
        const isBlind = this.getAttribute("data-is-blind") === "true"
        document.getElementById("receiverId").value = userId
        document.getElementById("isBlindDate").value = isBlind
        const modal = new bootstrap.Modal(document.getElementById("dateRequestModal"))
        modal.show()
      })
    })

    // Add event listener for modal close buttons
    document.querySelectorAll('[data-bs-dismiss="modal"]').forEach((button) => {
      button.addEventListener("click", function () {
        const modalElement = this.closest(".modal")
        hideModal(modalElement)
      })
    })
  }

  function hideModal(modalElement) {
    const modalInstance = bootstrap.Modal.getInstance(modalElement)
    if (modalInstance) {
      modalInstance.hide()
    }
    document.body.classList.remove("modal-open")
    document.body.style.overflow = ""
    document.body.style.paddingRight = ""
    const modalBackdrop = document.querySelector(".modal-backdrop")
    if (modalBackdrop) {
      modalBackdrop.remove()
    }
  }

  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault()
      updateUsers()
    })
  }

  if (filterForm) {
    filterForm.addEventListener("submit", (e) => {
      e.preventDefault()
      if (window.location.pathname === "/blind_dates") {
        updateBlindDates()
      } else {
        updateUsers()
      }
    })
  }

  // Add event listeners for real-time filtering
  if (searchInput) {
    searchInput.addEventListener("input", updateUsers)
  }

  if (filterForm) {
    const filterInputs = filterForm.querySelectorAll("select")
    filterInputs.forEach((input) => {
      input.addEventListener("change", () => {
        if (window.location.pathname === "/blind_dates") {
          updateBlindDates()
        } else {
          updateUsers()
        }
      })
    })
  }

  // Initial load of users
  if (window.location.pathname === "/users") {
    updateUsers()
  } else if (window.location.pathname === "/blind_dates") {
    updateBlindDates()
  }

  attachButtonListeners()

  const editProfileBtn = document.getElementById("editProfileBtn")
  const profileView = document.getElementById("profileView")
  const profileEditForm = document.getElementById("profileEditForm")
  const cancelEditBtn = document.getElementById("cancelEdit")

  if (editProfileBtn && profileView && profileEditForm) {
    editProfileBtn.addEventListener("click", () => {
      profileView.classList.add("d-none")
      profileEditForm.classList.remove("d-none")
    })

    cancelEditBtn.addEventListener("click", () => {
      profileView.classList.remove("d-none")
      profileEditForm.classList.add("d-none")
    })

    profileEditForm.addEventListener("submit", (e) => {
      e.preventDefault()
      const formData = new FormData(profileEditForm)

      formData.append("state", document.getElementById("state").value)
      formData.append("cgpa", document.getElementById("cgpa").value)

      fetch("/update_profile", {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((err) => {
              throw err
            })
          }
          return response.json()
        })
        .then((data) => {
          alert(data.message)
          location.reload()
        })
        .catch((error) => {
          console.error("Error:", error)
          alert("An error occurred while updating your profile: " + (error.error || "Unknown error"))
        })
    })
  }

  // Add event listeners for confession likes
  const likeButtons = document.querySelectorAll(".btn-like")
  likeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const confessionId = this.getAttribute("data-confession-id")
      const icon = this.querySelector("i")
      const likeCount = this.querySelector(".like-count")

      fetch(`/like_confession/${confessionId}`, {
        method: "POST",
      })
        .then((response) => {
          if (!response.ok) {
            if (response.status === 401) {
              alert("Please login to like confessions")
              return
            }
            throw new Error("Network response was not ok")
          }
          return response.json()
        })
        .then((data) => {
          likeCount.textContent = data.likes
          if (data.liked) {
            this.classList.add("liked")
            icon.classList.remove("bi-heart")
            icon.classList.add("bi-heart-fill")
          } else {
            this.classList.remove("liked")
            icon.classList.remove("bi-heart-fill")
            icon.classList.add("bi-heart")
          }
        })
        .catch((error) => {
          console.error("Error:", error)
          alert("An error occurred while processing your like")
        })
    })
  })

  function setupSocietyCheckboxes() {
    const societyCheckboxes = document.querySelectorAll("[data-society-checkbox]")
    const noneCheckbox = document.getElementById("society_none")

    if (societyCheckboxes && noneCheckbox) {
      function updateCheckboxes() {
        const anyChecked = Array.from(societyCheckboxes).some((cb) => cb.checked)
        noneCheckbox.disabled = anyChecked
        if (anyChecked) {
          noneCheckbox.checked = false
        }
      }

      societyCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", updateCheckboxes)
      })

      noneCheckbox.addEventListener("change", function () {
        if (this.checked) {
          societyCheckboxes.forEach((cb) => {
            cb.checked = false
            cb.disabled = true
          })
        } else {
          societyCheckboxes.forEach((cb) => {
            cb.disabled = false
          })
        }
      })

      // Initial setup
      updateCheckboxes()
    }
  }

  setupSocietyCheckboxes()

  // Terms and Conditions checkbox handler
  const acceptTermsCheckbox2 = document.getElementById("acceptTerms")
  const signupButton = document.getElementById("signupButton")

  if (acceptTermsCheckbox2 && signupButton) {
    acceptTermsCheckbox2.addEventListener("change", function () {
      signupButton.disabled = !this.checked
    })
  }
})

