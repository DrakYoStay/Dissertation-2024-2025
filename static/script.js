let videoStream;
const video = document.getElementById('video');

if (video) {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
      videoStream = stream;
    })
    .catch(err => alert("Camera access denied."));
}

function showMessage(msg) {
  const status = document.getElementById('status-message');
  if (status) status.textContent = msg;
}

function stopCamera() {
  if (videoStream) {
    videoStream.getTracks().forEach(track => track.stop());
  }
}

function captureImage() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0);
  return canvas.toDataURL('image/jpeg');
}

function register() {
  const name = document.getElementById('username').value;
  if (!name) return alert("Enter your name.");
  
  showMessage("Get ready... Please blink!");

  setTimeout(() => {
    const image = captureImage();

    fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, image })
    })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      alert(body.message);
      stopCamera();
      if (status === 200) {
      window.location.href = '/login-page';
      } else {
        restartCamera();
        showMessage("Try again. Make sure you blink!");
      }
    })
    .catch(err => alert("Registration failed: " + err.message));
  }, 1500);
}

function login() {
  const name = document.getElementById('username').value;
  if (!name) return alert("Enter your username.");

  showMessage("Get ready... Please blink!");

  setTimeout(() => {
    const image = captureImage();

    fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, image })
    })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      alert(body.message);
      if (status === 200) {
        stopCamera();
        window.location.href = '/';
      } else {
        restartCamera();
        showMessage("Try again. Make sure you blink!");
      }
    })
    .catch(err => alert("Login failed: " + err.message));
  }, 1500);
}

function restartCamera() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
      videoStream = stream;
    })
    .catch(err => alert("Unable to restart camera."));
}
