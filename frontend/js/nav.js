// Nav rendering
function renderNav() {
  const isLog = isLoggedIn();
  const html = `
    <nav class="navbar">
      <div class="nav-inner">
        <div class="nav-brand">
          <div class="nav-logo">🛕</div>
          <div class="nav-name">
            TTD
            <small>Tirumala Tirupati Devasthanams</small>
          </div>
        </div>
        <ul class="nav-links" id="navLinks">
          <li><a href="index.html">Home</a></li>
          <li><a href="darshan.html">Darshan</a></li>
          <li><a href="accommodation.html">Accommodation</a></li>
          <li><a href="donation.html">e-Hundi</a></li>
          ${isLog 
            ? `<li><a href="dashboard.html" class="nav-cta">My Dashboard</a></li>`
            : `<li><a href="login.html">Login</a></li><li><a href="register.html" class="nav-cta">Register</a></li>`
          }
        </ul>
        <div class="hamburger" id="hamburger">
          <span></span><span></span><span></span>
        </div>
      </div>
      <div class="gold-bar"></div>
    </nav>
  `;
  document.getElementById('nav-placeholder').innerHTML = html;

  // Active state
  const path = window.location.pathname;
  const links = document.querySelectorAll('.nav-links a');
  links.forEach(l => {
    if (path.includes(l.getAttribute('href')) && l.getAttribute('href') !== 'index.html') {
      l.classList.add('active');
    } else if (path.endsWith('/') && l.getAttribute('href') === 'index.html') {
      l.classList.add('active');
    }
  });

  // Hamburger
  const ham = document.getElementById('hamburger');
  if (ham) {
    ham.addEventListener('click', () => {
      document.getElementById('navLinks').classList.toggle('open');
    });
  }
}

document.addEventListener('DOMContentLoaded', renderNav);
