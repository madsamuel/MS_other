chrome.runtime.onInstalled.addListener(() => {
    console.log("Plugin installed.");
  });
  
  chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => alert('Hello from the plugin!')
    });
  });
  