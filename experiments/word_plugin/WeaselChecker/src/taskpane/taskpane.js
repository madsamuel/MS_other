import { weaselWords } from "./weaselWords";
Office.onReady(() => {
  console.log("✅ Office is ready");

  document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ DOM ready");
    const btn = document.getElementById("checkBtn");
    if (btn) {
      console.log("✅ Button found");
      btn.addEventListener("click", findWeaselWords);
    } else {
      console.error("❌ Button not found");
    }
  });
});

async function findWeaselWords() {
  console.log("🔍 findWeaselWords called");

  try {
    await Word.run(async (context) => {
      const body = context.document.body;
      body.load("text");
      await context.sync();

      const text = body.text;
      console.log("📝 Document text:", text);

      const foundWords = weaselWords.filter(word =>
        new RegExp(`\\b${word}\\b`, "gi").test(text)
      );

      const resultEl = document.getElementById("results");
      if (foundWords.length > 0) {
        const unique = [...new Set(foundWords)];
        resultEl.textContent = "Weasel words found: " + unique.join(", ");
      } else {
        resultEl.textContent = "No weasel words found!";
      }
    });
  } catch (error) {
    console.error("❌ Error in findWeaselWords:", error);
    alert("Error: " + error.message);
  }
}