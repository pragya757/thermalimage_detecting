const openWebcamButton = document.getElementById('open-webcam');
const captureImageButton = document.getElementById('capture-image');
const diseasesListButton = document.getElementById('diseases-list');
const diseaseListSection = document.getElementById('disease-list-section');
const webcamPreview = document.getElementById('webcam-preview');
const webcamElement = document.getElementById('webcam');
const canvasElement = document.getElementById('canvas');

// Open webcam functionality
openWebcamButton.addEventListener('click', () => {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        webcamElement.srcObject = stream;
        webcamPreview.style.display = 'block';
      })
      .catch(err => {
        alert('Error accessing webcam: ' + err);
      });
  }
});

// Capture image functionality
captureImageButton.addEventListener('click', () => {
  const context = canvasElement.getContext('2d');
  context.drawImage(webcamElement, 0, 0, canvasElement.width, canvasElement.height);
  // Here, you can send image data to the backend for thermal detection
  alert('Image Captured! Now connect the backend to process the thermal image.');
});

// Show diseases list functionality
diseasesListButton.addEventListener('click', () => {
  diseaseListSection.style.display = diseaseListSection.style.display === 'none' ? 'block' : 'none';
});
