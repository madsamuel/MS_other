import { weaselWords } from "./weaselWords";

// ✅ Protect Office-dependent code from running in non-Office context
if (typeof Office !== "undefined" && Office.onReady) {
  Office.onReady().then(() => {
    console.log("✅ Office.js is loaded and ready");

    document.addEventListener("DOMContentLoaded", () => {
      const btn = document.getElementById("checkBtn");
      if (btn) {
        btn.addEventListener("click", findWeaselWords);
      }
    });
  });
} else {
  console.warn("⚠️ Office.js not available — this is probably a browser preview.");
}

async function findWeaselWords() {
  try {
    await Word.run(async (context) => {
      const body = context.document.body;
      body.load("text");
      await context.sync();

      const found = weaselWords.filter(word =>
        new RegExp(`\\b${word}\\b`, "gi").test(body.text)
      );

      const result = document.getElementById("results");
      result.textContent = found.length
        ? `Weasel words found: ${[...new Set(found)].join(", ")}`
        : "No weasel words found.";
    });
  } catch (error) {
    console.error("❌ Error:", error);
    alert("Something went wrong: " + error.message);
  }
}
