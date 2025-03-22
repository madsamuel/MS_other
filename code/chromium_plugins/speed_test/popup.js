document.getElementById('startButton').addEventListener('click', function() {
  const resultDiv = document.getElementById('result');
  resultDiv.textContent = "Testing...";
  
  // Replace this with your own test file URL
  const testFileUrl = "https://yourdomain.com/testfile.bin?cb=" + Date.now();
  
  // Known file size in bytes; adjust according to your test file's size.
  const fileSize = 1048576; // For example, 1MB = 1048576 bytes
  
  const startTime = performance.now();
  
  fetch(testFileUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.blob();
    })
    .then(() => {
      const duration = (performance.now() - startTime) / 1000; // seconds
      const bitsLoaded = fileSize * 8; // convert bytes to bits
      const speedBps = bitsLoaded / duration; // bits per second
      const speedMbps = (speedBps / (1024 * 1024)).toFixed(2);
      resultDiv.textContent = "Download speed: " + speedMbps + " Mbps";
    })
    .catch(error => {
      console.error("Error:", error);
      resultDiv.textContent = "Error loading test file. Please try again.";
    });
});
