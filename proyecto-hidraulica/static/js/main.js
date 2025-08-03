setTimeout(() => {
  const intro = document.getElementById('intro');
  const mainSection = document.querySelector('section');

  intro.style.display = 'none';        // Oculta overlay
  mainSection.classList.add('visible'); // Inicia fade-in
}, 4000);
