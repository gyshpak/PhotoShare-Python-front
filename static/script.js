document.addEventListener('mousemove', (event) => {
    const { clientX: x, clientY: y } = event;
    createStar(x, y);
    moveCursorGlow(x, y);
});

function createStar(x, y) {
    const star = document.createElement('div');
    star.classList.add('star');
    const offsetX = window.pageXOffset;
    const offsetY = window.pageYOffset;
    
    star.style.left = `${x + offsetX}px`;
    star.style.top = `${y + offsetY}px`;
    document.body.appendChild(star);
    star.addEventListener('animationend', () => {
        star.remove();
    });
}

function moveCursorGlow(x, y) {
    let cursorGlow = document.getElementById('cursor-glow');
    if (!cursorGlow) {
        cursorGlow = document.createElement('div');
        cursorGlow.id = 'cursor-glow';
        document.body.appendChild(cursorGlow);
    }
    
    const offsetX = window.pageXOffset;
    const offsetY = window.pageYOffset;
    
    cursorGlow.style.left = `${x + offsetX}px`;
    cursorGlow.style.top = `${y + offsetY}px`;
}





  document.addEventListener('DOMContentLoaded', () => {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';

    const loginButton = document.getElementById('loginButton');
    const signupButton = document.getElementById('signupButton');
    const userButtons = document.getElementById('userButtons');

    if (isLoggedIn) {
        loginButton.style.display = 'none';
        signupButton.style.display = 'none';
        userButtons.style.display = 'block';
    } else {
        loginButton.style.display = 'block';
        signupButton.style.display = 'block';
        userButtons.style.display = 'none';
    }
});

function login() {
    localStorage.setItem('isLoggedIn', 'true');
    window.location.reload();
}

function logout() {
    localStorage.setItem('isLoggedIn', 'false');
    window.location.reload();
}