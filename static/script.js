// document.addEventListener('mousemove', (event) => {
//     createStar(event.clientX, event.clientY);
//   });
  
//   function createStar(x, y) {
//     const star = document.createElement('div');
//     star.classList.add('star');
//     star.style.left = `${x}px`;
//     star.style.top = `${y}px`;
//     document.body.appendChild(star);
  
//     // Remove the star after the animation is complete
//     star.addEventListener('animationend', () => {
//       star.remove();
//     });
//   }


document.addEventListener('mousemove', (event) => {
    const { clientX: x, clientY: y } = event;
    createStar(x, y);
    moveCursorGlow(x, y);
  });
  
  function createStar(x, y) {
    const star = document.createElement('div');
    star.classList.add('star');
    star.style.left = `${x}px`;
    star.style.top = `${y}px`;
    document.body.appendChild(star);
  
    // Remove the star after the animation is complete
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
    cursorGlow.style.left = `${x}px`;
    cursorGlow.style.top = `${y}px`;
  }





  document.addEventListener('DOMContentLoaded', () => {
    // Check if the user is logged in
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

// Mock function to simulate login (replace this with your actual login logic)
function login() {
    localStorage.setItem('isLoggedIn', 'true');
    window.location.reload();
}

// Mock function to simulate logout
function logout() {
    localStorage.setItem('isLoggedIn', 'false');
    window.location.reload();
}







// document.addEventListener('DOMContentLoaded', () => {
//     const buttons = document.querySelectorAll('a');

//     buttons.forEach(button => {
//         button.addEventListener('click', (e) => {
//             // Redirect to the href immediately
//             window.location.href = button.href;

//             e.preventDefault(); // Prevent default link behavior for demo purposes
//             const numStars = 60;
//             const rect = button.getBoundingClientRect();
//             const buttonCenterX = rect.left + rect.width / 2;
//             const buttonCenterY = rect.top + rect.height / 2;

//             for (let i = 0; i < numStars; i++) {
//                 const star = document.createElement('div');
//                 star.classList.add('star');
//                 document.body.appendChild(star);

//                 const angle = Math.random() * 2 * Math.PI;
//                 const radius = Math.random() * 100;
//                 const translateX = radius * Math.cos(angle);
//                 const translateY = radius * Math.sin(angle);

//                 star.style.setProperty('--translate-x', `${translateX}px`);
//                 star.style.setProperty('--translate-y', `${translateY}px`);
//                 star.style.left = `${buttonCenterX}px`;
//                 star.style.top = `${buttonCenterY}px`;

//                 star.addEventListener('animationend', () => {
//                     star.remove();
//                 });
//             }
//         });
//     });
// });



// document.addEventListener('DOMContentLoaded', () => {
//     const buttons = document.querySelectorAll('a');

//     buttons.forEach(button => {
//         button.addEventListener('click', (e) => {
//             const numStars = 60;
//             const rect = button.getBoundingClientRect();
//             const buttonCenterX = rect.left + rect.width / 2;
//             const buttonCenterY = rect.top + rect.height / 2;

//             for (let i = 0; i < numStars; i++) {
//                 const star = document.createElement('div');
//                 star.classList.add('star');
//                 document.body.appendChild(star);

//                 const angle = Math.random() * 2 * Math.PI;
//                 const radius = Math.random() * 100;
//                 const translateX = radius * Math.cos(angle);
//                 const translateY = radius * Math.sin(angle);

//                 star.style.setProperty('--translate-x', `${translateX}px`);
//                 star.style.setProperty('--translate-y', `${translateY}px`);
//                 star.style.left = `${buttonCenterX}px`;
//                 star.style.top = `${buttonCenterY}px`;

//                 star.addEventListener('animationend', () => {
//                     star.remove();
//                 });
//             }
//         });
//     });
// });



// document.addEventListener('DOMContentLoaded', () => {
//     const links = document.querySelectorAll('a');

//     links.forEach(link => {
//         link.addEventListener('mousedown', (e) => {
//             const numStars = 60;
//             const rect = link.getBoundingClientRect();
//             const linkCenterX = rect.left + rect.width / 2;
//             const linkCenterY = rect.top + rect.height / 2;

//             for (let i = 0; i < numStars; i++) {
//                 const star = document.createElement('div');
//                 star.classList.add('star');
//                 document.body.appendChild(star);

//                 const angle = Math.random() * 2 * Math.PI;
//                 const radius = Math.random() * 100;
//                 const translateX = radius * Math.cos(angle);
//                 const translateY = radius * Math.sin(angle);

//                 star.style.setProperty('--translate-x', `${translateX}px`);
//                 star.style.setProperty('--translate-y', `${translateY}px`);
//                 star.style.left = `${linkCenterX}px`;
//                 star.style.top = `${linkCenterY}px`;

//                 star.addEventListener('animationend', () => {
//                     star.remove();
//                 });
//             }
//         });
//     });
// });





// document.addEventListener('DOMContentLoaded', () => {
//     const links = document.querySelectorAll('a');

//     links.forEach(link => {
//         link.addEventListener('click', (e) => {
//             e.preventDefault(); // Відмінити стандартну поведінку посилання

//             setTimeout(() => {
//                 window.location.href = link.href; // Редірект після паузи
//             }, 400);
            
//             const numStars = 60;
//             const rect = link.getBoundingClientRect();
//             const linkCenterX = rect.left + rect.width / 2;
//             const linkCenterY = rect.top + rect.height / 2;

//             for (let i = 0; i < numStars; i++) {
//                 const star = document.createElement('div');
//                 star.classList.add('star');
//                 document.body.appendChild(star);

//                 const angle = Math.random() * 2 * Math.PI;
//                 const radius = Math.random() * 100;
//                 const translateX = radius * Math.cos(angle);
//                 const translateY = radius * Math.sin(angle);

//                 star.style.setProperty('--translate-x', `${translateX}px`);
//                 star.style.setProperty('--translate-y', `${translateY}px`);
//                 star.style.left = `${linkCenterX}px`;
//                 star.style.top = `${linkCenterY}px`;

//                 star.addEventListener('animationend', () => {
//                     star.remove();
//                 });
//             }
//         });
//     });
// });








document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.magic-button');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });
});




document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('a');

    buttons.forEach(button => {
            if (button.classList.contains('active')) {
                const numStars = 60;
                const rect = button.getBoundingClientRect();
                const buttonCenterX = rect.left + rect.width / 2;
                const buttonCenterY = rect.top + rect.height / 2;

                for (let i = 0; i < numStars; i++) {
                    const star = document.createElement('div');
                    star.classList.add('star');
                    document.body.appendChild(star);

                    const angle = Math.random() * 2 * Math.PI;
                    const radius = Math.random() * 100;
                    const translateX = radius * Math.cos(angle);
                    const translateY = radius * Math.sin(angle);

                    star.style.setProperty('--translate-x', `${translateX}px`);
                    star.style.setProperty('--translate-y', `${translateY}px`);
                    star.style.left = `${buttonCenterX}px`;
                    star.style.top = `${buttonCenterY}px`;
                }
            }
    });
});