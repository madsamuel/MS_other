import { weaselWords } from "./weaselWords";


Office.onReady(() => {
  console.log("✅ Office.js is loaded and ready");

  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("checkBtn");
    if (btn) {
      btn.addEventListener("click", findWeaselWords);
    }
  });
});

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