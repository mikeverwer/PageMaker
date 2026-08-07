const navs = document.getElementsByClassName('main-links');
let links = [];
const currentUrl = window.location.href.split("#")[0];

for (const nav of navs) {
    const navLinks = nav.getElementsByTagName('a');
    links = [...links, ...navLinks];
}

for (let i = 0; i < links.length; i++) {
    const link = links[i].href.split('#')[0];
    if (link === currentUrl) {
        links[i].classList.add('current');
    }
    else {
        links[i].classList.remove('current');
    }
}
