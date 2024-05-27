document.addEventListener('mousemove', (event) => {
    const { clientX: x, clientY: y } = event;
    createStar(x, y);
    moveCursorGlow(x, y);
});

// function createStar(x, y) {
//     const star = document.createElement('div');
//     star.classList.add('star');
//     const offsetX = window.pageXOffset;
//     const offsetY = window.pageYOffset;
    
//     star.style.left = `${x + offsetX}px`;
//     star.style.top = `${y + offsetY}px`;
//     document.body.appendChild(star);
//     star.addEventListener('animationend', () => {
//         star.remove();
//     });
// }

function createStar(x, y) {
    const numStars = 1;

    for (let i = 0; i < numStars; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        const offsetX = window.pageXOffset;
        const offsetY = window.pageYOffset;
        
        const randomX = Math.random() * 1 - 1;
        const randomY = Math.random() * 1 - 1;

        star.style.left = `${x + offsetX + randomX}px`;
        star.style.top = `${y + offsetY + randomY}px`;
        document.body.appendChild(star);

        star.addEventListener('animationend', () => {
            star.remove();
        });
    }
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


















document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.photo-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const { clientX, clientY } = e;
            const { left, top, width, height } = card.getBoundingClientRect();

            // Знаходимо положення курсора відносно середини карточки
            const xPos = (clientX - (left + width / 2)) / (width / 2);
            const yPos = (clientY - (top + height / 2)) / (height / 2);

            // Обертаємо карточку з урахуванням положення курсора
            card.style.transform = `rotateY(${xPos * 10}deg) rotateX(${-yPos * 10}deg)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'rotateX(0deg) rotateY(0deg)';
        });
    });
});



function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const togglePassword = document.querySelector('.toggle-password');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        togglePassword.textContent = '🙈';
    } else {
        passwordInput.type = 'password';
        togglePassword.textContent = '👁️';
    }
}