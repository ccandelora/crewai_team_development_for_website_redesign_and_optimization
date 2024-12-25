document.addEventListener('DOMContentLoaded', function() {
// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
anchor.addEventListener('click', function (e) {
e.preventDefault();
const target = document.querySelector(this.getAttribute('href'));
if (target) {
target.scrollIntoView({
behavior: 'smooth',
block: 'start'
});
}
});
});

// Mobile navigation toggle
const nav = document.querySelector('.nav-links');
const toggleButton = document.createElement('button');
toggleButton.classList.add('nav-toggle');
toggleButton.innerHTML = '☰';
toggleButton.addEventListener('click', () => {
nav.classList.toggle('active');
});
document.querySelector('.main-nav').prepend(toggleButton);
});