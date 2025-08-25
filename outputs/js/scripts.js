// Set the initial image index to 1
var currentImageIndex = getRandomInt(1, 4);
var intervalId;

// ███████ ██    ██ ███    ██  ██████ ████████ ██  ██████  ███    ██ ███████ 
// ██      ██    ██ ████   ██ ██         ██    ██ ██    ██ ████   ██ ██      
// █████   ██    ██ ██ ██  ██ ██         ██    ██ ██    ██ ██ ██  ██ ███████ 
// ██      ██    ██ ██  ██ ██ ██         ██    ██ ██    ██ ██  ██ ██      ██ 
// ██       ██████  ██   ████  ██████    ██    ██  ██████  ██   ████ ███████ 
                                          
// -------------------------------------------------------------------------------------------
// Animates the `home` icon and sets it to a random frame on page load.
// -------------------------------------------------------------------------------------------

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Function to set the source of the header image
function setHeaderImage() {
    var imagePath = "/assets/images/website-icon-" + currentImageIndex + ".png";
    document.getElementById("home-button").src = imagePath;

    // Increment the image index
    currentImageIndex++;

    // Reset to 1 if it exceeds the maximum value (4 in this case)
    if (currentImageIndex > 4) {
        currentImageIndex = 1;
    }
}

// -------------------------------------------------------------------------------------------
// Toggle the Navbars
// -------------------------------------------------------------------------------------------
// Determine if both panels are hidden and update the 'zen-mode' button accordingly
function updateHideButton(navBars, beforeCheck) {
    const button = document.querySelector('button');
    let closedBraces = '{ }';
    let openBraces = '}{';
    let bothHidden = true; // Assume both are hidden initially
    if (beforeCheck) {
        closedBraces = '}{'
        openBraces = '{ }'
    }
    navBars.forEach(function (navBar) {
        if (navBar.style.display !== 'none') {
            bothHidden = false; // If any navbar is visible, both are not hidden
        }
    });
    if (bothHidden) {
        button.textContent = openBraces;
    } else {
        button.textContent = closedBraces;
    }
    return bothHidden; // Return the status of both navbars
}

// Hide or show both navbars based on the button state
function toggleNavBars(navBars, hidden) {
    navBars.forEach(function (navBar) {
        if (hidden) {
            navBar.style.display = 'flex'; // Show the navbar
        } else {
            navBar.style.display = 'none'; // Hide the navbar
        }
    });
}

// Hide the respective navbar if the left or right edge has been clicked
function toggleNavBar(event) {
    const leftNav = document.getElementById('leftNav');
    const rightNav = document.getElementById('rightNav');
    const panelID = event.target.id;
    let navBar;
    if (panelID === 'left-side') {
        navBar = leftNav;
    } else if (panelID === 'right-side') {
        navBar = rightNav;
    } else {
        // const navBars = document.querySelectorAll('nav');
        const navBars = [leftNav, rightNav];
        const hidden = updateHideButton(navBars, true); // Toggle the visibility of navbars and update button text
        toggleNavBars(navBars, hidden); // Hide or show both navbars based on the button state
        return; // Exit the function since no further action is needed
    }
    if (navBar.style.display === 'none') {
        navBar.style.display = 'block'; // Show the navbar
    } else {
        navBar.style.display = 'none'; // Hide the navbar
    }
    updateHideButton(document.querySelectorAll('nav'), false); // Update the button text
}

// ██████   ██████  ███    ███     ██       ██████   █████  ██████  ███████ ██████  
// ██   ██ ██    ██ ████  ████     ██      ██    ██ ██   ██ ██   ██ ██      ██   ██ 
// ██   ██ ██    ██ ██ ████ ██     ██      ██    ██ ███████ ██   ██ █████   ██   ██ 
// ██   ██ ██    ██ ██  ██  ██     ██      ██    ██ ██   ██ ██   ██ ██      ██   ██ 
// ██████   ██████  ██      ██     ███████  ██████  ██   ██ ██████  ███████ ██████

document.addEventListener('DOMContentLoaded', function () {
    // -------------------------------------------------------------------------------------------
    // Set the home button icon and animate the glider on hover.
    // -------------------------------------------------------------------------------------------
    window.onload = setHeaderImage;
    document.getElementById("home-button").addEventListener("mouseover", function () {
        setHeaderImage;
        intervalId = setInterval(setHeaderImage, 387.1); // Call setHeaderImage every 1/2 second
    });
    document.getElementById("home-button").addEventListener("mouseout", function () {
        clearInterval(intervalId); // Stop calling setHeaderImage
    });
    
    // -------------------------------------------------------------------------------------------
    // Toggle the navbars via side-panels or button.
    // -------------------------------------------------------------------------------------------
    const panelToggleAreas = document.querySelectorAll('.panel-toggle-area');
    const button = document.querySelector('button');
    panelToggleAreas.forEach(function (toggleArea) {  // Add event listener to side panels
        toggleArea.addEventListener('click', toggleNavBar);
    });
    button.addEventListener('click', toggleNavBar); // Add event listener to the button
});
