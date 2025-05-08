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

function restartCamera() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
      videoStream = stream;
    })
    .catch(err => alert("Unable to restart camera."));
}

// ✅ NEW: Capture ~20 frames over 2 seconds
function captureFrames(duration = 2000, interval = 100) {
  return new Promise((resolve) => {
    const frames = [];
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const capture = () => {
      ctx.drawImage(video, 0, 0);
      frames.push(canvas.toDataURL('image/jpeg'));
    };

    const intervalId = setInterval(capture, interval);

    setTimeout(() => {
      clearInterval(intervalId);
      resolve(frames);
    }, duration);
  });
}

function register() {
  const name = document.getElementById('username').value;
  if (!name) return alert("Enter your name.");

  showMessage("Recording... Please blink and move!");

  captureFrames().then(frames => {
    console.log("Captured frames:", frames.length);
    fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, frames })
    })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      alert(body.message);
      stopCamera();
      if (status === 200) {
        window.location.href = '/login-page';
      } else {
        restartCamera();
        showMessage("Try again. Make sure you blink and move!");
      }
    })
    .catch(err => alert("Registration failed: " + err.message));
  });
}

function login() {
  const name = document.getElementById('username').value;
  if (!name) return alert("Enter your username.");

  showMessage("Recording... Please blink and move!");

  captureFrames().then(frames => {
    console.log("Captured frames:", frames.length);
    fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, frames })
    })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      alert(body.message);
      if (status === 200) {
        stopCamera();
        window.location.href = '/';
      } else {
        restartCamera();
        showMessage("Try again. Make sure you blink and move!");
      }
    })
    .catch(err => alert("Login failed: " + err.message));
  });
}
