function setAppHeight() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--app-vh', `${vh}px`);
}

setAppHeight();

window.addEventListener('resize', setAppHeight);
window.addEventListener('orientationchange', setAppHeight);