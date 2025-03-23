// Wait for the DOM to be fully loaded.
document.addEventListener("DOMContentLoaded", () => {
  const startButton = document.getElementById('startButton');
  const resultDiv = document.getElementById('result');

  // Check if the required elements exist.
  if (!startButton || !resultDiv) {
    console.error("Required elements are missing from the HTML.");
    return;
  }

  startButton.addEventListener('click', async () => {
    // Disable the button to prevent multiple clicks during the test.
    startButton.disabled = true;
    resultDiv.textContent = "Testing...";

    // Construct the test file URL with a cache-busting parameter.
    const testFileUrl = "https://raw.githubusercontent.com/madsamuel/MS_other/master/non_code/pre%202022/Events/MS%20Build%202019/Optimizing%20your%20applications%20for%20Windows%20Virtual%20Desktop%20-%20BRK3076%20-%20Copy%20part%201.mp4?cb=" + Date.now();
    const startTime = performance.now();

    try {
      // Fetch the file.
      const response = await fetch(testFileUrl);
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      // Download the file as a blob.
      const blob = await response.blob();

      // Use the blob size to calculate speed.
      const fileSize = blob.size; // in bytes
      const duration = (performance.now() - startTime) / 1000; // in seconds
      const bitsLoaded = fileSize * 8; // convert bytes to bits
      const speedBps = bitsLoaded / duration; // bits per second
      const speedMbps = (speedBps / (1024 * 1024)).toFixed(2); // convert to Mbps

      resultDiv.textContent = "Download speed: " + speedMbps + " Mbps";
    } catch (error) {
      console.error("Error:", error);
      resultDiv.textContent = "Error loading test file. Please try again.";
    } finally {
      // Re-enable the button once the test completes.
      startButton.disabled = false;
    }
  });
});
