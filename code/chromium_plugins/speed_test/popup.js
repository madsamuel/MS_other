document.getElementById('startButton').addEventListener('click', function() {
  const resultDiv = document.getElementById('result');
  resultDiv.textContent = "Testing...";
  
  // Using the raw URL for the GitHub-hosted video file.
  const testFileUrl = "https://raw.githubusercontent.com/madsamuel/MS_other/master/non_code/pre%202022/Events/MS%20Build%202019/Optimizing%20your%20applications%20for%20Windows%20Virtual%20Desktop%20-%20BRK3076%20-%20Copy%20part%201.mp4?cb=" + Date.now();

  const startTime = performance.now();

  fetch(testFileUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.blob();
    })
    .then(blob => {
      // Get the actual file size from the blob.
      const fileSize = blob.size; // in bytes
      const duration = (performance.now() - startTime) / 1000; // seconds
      const bitsLoaded = fileSize * 8; // convert bytes to bits
      const speedBps = bitsLoaded / duration; // bits per second
      const speedMbps = (speedBps / (1024 * 1024)).toFixed(2); // convert to Mbps
      resultDiv.textContent = "Download speed: " + speedMbps + " Mbps";
    })
    .catch(error => {
      console.error("Error:", error);
      resultDiv.textContent = "Error loading test file. Please try again.";
    });
});
