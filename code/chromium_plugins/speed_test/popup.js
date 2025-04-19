document.addEventListener("DOMContentLoaded", () => {
  const startButton = document.getElementById('startButton');
  const spinner = document.getElementById('spinner');
  const resultDiv = document.getElementById('result');

  startButton.addEventListener('click', async () => {
    // Disable the button and show the spinner
    startButton.disabled = true;
    spinner.style.display = 'block';
    resultDiv.textContent = "Testing...";
222222
    const testFileUrl = "https://raw.githubusercontent.com/madsamuel/MS_other/master/non_code/pre%202022/Events/MS%20Build%202019/Optimizing%20your%20applications%20for%20Windows%20Virtual%20Desktop%20-%20BRK3076%20-%20Copy%20part%201.mp4?cb=" + Date.now();

    const startTime = performance.now();

    try {
      const response = await fetch(testFileUrl);
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const blob = await response.blob();
      const fileSize = blob.size; // in bytes222222
      const duration = (performance.now() - startTime) / 1000; // seconds
      const bitsLoaded = fileSize * 8; // bytes -> bits
      const speedBps = bitsLoaded / duration;
      const speedMbps = (speedBps / (1024 * 1024)).toFixed(2);

      // (Optional) Color-code the result based on speed
      if (speedMbps > 100) {
        resultDiv.style.color = "green";
      } else if (speedMbps < 10) {
        resultDiv.style.color = "red";
      } else {
        resultDiv.style.color = "#333";
      }

      resultDiv.textContent = "Download speed: " + speedMbps + " Mbps";
    } catch (error) {
      console.error("Error:", error);
      resultDiv.style.color = "red";
      resultDiv.textContent = "Error loading test file.";
    } finally {
      // Hide the spinner and re-enable the button
      spinner.style.display = 'none';
      startButton.disabled = false;
    }
  });
});
