const { getData } = require("./_github");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  
  if (req.method === "OPTIONS") return res.status(200).end();
  
  try {
    const { entries } = await getData();
    return res.status(200).json({ success: true, data: entries });
  } catch (err) {
    console.error("Error fetching data:", err.message);
    return res.status(500).json({ success: false, error: err.message });
  }
};
