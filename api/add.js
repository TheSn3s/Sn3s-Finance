const { getData, saveData } = require("./_github");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const { date, client, project, amount, payment_status, category, description } = req.body;
    const { entries, sha } = await getData();

    // Find next serial
    let maxSerial = 0;
    entries.forEach((e) => {
      const n = parseInt(e.Notes);
      if (!isNaN(n) && n > maxSerial) maxSerial = n;
    });
    const newSerial = String(maxSerial + 1).padStart(3, "0");

    const newEntry = {
      Date: date || new Date().toISOString().split("T")[0],
      Category: category || "Video",
      Client: client || "",
      Project: project || "",
      Status: "Delivered",
      Amount: String(amount || "0"),
      PaymentStatus: payment_status || "Not Paid",
      Description: description || "",
      Notes: newSerial,
    };

    entries.push(newEntry);
    await saveData(entries, sha, `➕ Add invoice #${newSerial}: ${client} - ${project}`);

    return res.status(200).json({ success: true, serial: newSerial });
  } catch (err) {
    console.error("Error adding entry:", err.message);
    return res.status(500).json({ success: false, error: err.message });
  }
};
