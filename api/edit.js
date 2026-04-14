const { getData, saveData } = require("./_github");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const { notes, date, client, project, amount, payment_status, description } = req.body;
    if (!notes) return res.status(400).json({ error: "Missing serial (notes)" });

    const { entries, sha } = await getData();

    const idx = entries.findIndex((e) => e.Notes === notes);
    if (idx === -1) return res.status(404).json({ error: "Entry not found" });

    if (date) entries[idx].Date = date;
    if (client) entries[idx].Client = client;
    if (project) entries[idx].Project = project;
    if (amount !== undefined) entries[idx].Amount = String(amount);
    if (payment_status) entries[idx].PaymentStatus = payment_status;
    if (description !== undefined) entries[idx].Description = description;

    await saveData(entries, sha, `✏️ Edit invoice #${notes}`);

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error("Error editing entry:", err.message);
    return res.status(500).json({ success: false, error: err.message });
  }
};
