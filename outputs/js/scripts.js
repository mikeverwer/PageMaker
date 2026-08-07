// Set the initial image index to a random frame
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

function setHeaderImage() {
    var imagePath = "/assets/images/website-icon-" + currentImageIndex + ".png";
    document.getElementById("home-button").src = imagePath;

    currentImageIndex++;
    if (currentImageIndex > 4) {
        currentImageIndex = 1;
    }
}

// -------------------------------------------------------------------------------------------
// Toggle the sidebar navs via the { } button.
// -------------------------------------------------------------------------------------------

function toggleSidebars() {
    const button = document.getElementById("toggle-sidebars");
    const container = document.querySelector('.container');
    const navBars = [
        document.getElementById('leftNav'),
        document.getElementById('rightNav'),
    ];

    const currentlyHidden = navBars[0].classList.contains('hiding');

    container.classList.toggle('zen', !currentlyHidden);
    navBars.forEach(nav => nav.classList.toggle('hiding', !currentlyHidden));

    // Button flip animation 
    button.classList.add('flipping');
    setTimeout(() => {
        button.textContent = currentlyHidden ? '{ }' : '}{';
        button.classList.remove('flipping');
    }, 150);
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
    setHeaderImage();  // initial frame

    const homeButton = document.getElementById("home-button");
    homeButton.addEventListener("mouseover", function () {
        intervalId = setInterval(setHeaderImage, 400);
    });
    homeButton.addEventListener("mouseout", function () {
        clearInterval(intervalId);
    });

    // -------------------------------------------------------------------------------------------
    // Wire up the { } sidebar toggle button.
    // -------------------------------------------------------------------------------------------
    document
        .getElementById("toggle-sidebars")
        .addEventListener('click', toggleSidebars);
});