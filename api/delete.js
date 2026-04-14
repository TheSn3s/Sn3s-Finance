const { getData, saveData } = require("./_github");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const { notes } = req.body;
    if (!notes) return res.status(400).json({ error: "Missing serial (notes)" });

    const { entries, sha } = await getData();

    const filtered = entries.filter((e) => e.Notes !== notes);
    if (filtered.length === entries.length) {
      return res.status(404).json({ error: "Entry not found" });
    }

    await saveData(filtered, sha, `🗑️ Delete invoice #${notes}`);

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error("Error deleting entry:", err.message);
    return res.status(500).json({ success: false, error: err.message });
  }
};
