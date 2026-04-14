const { Octokit } = require("@octokit/rest");

const OWNER = "TheSn3s";
const REPO = "Sn3s-Finance";
const FILE_PATH = "data.json";
const BRANCH = "main";

function getOctokit() {
  return new Octokit({ auth: process.env.GITHUB_TOKEN });
}

async function getData() {
  const octokit = getOctokit();
  const { data } = await octokit.repos.getContent({
    owner: OWNER,
    repo: REPO,
    path: FILE_PATH,
    ref: BRANCH,
  });
  const content = Buffer.from(data.content, "base64").toString("utf-8");
  return { entries: JSON.parse(content), sha: data.sha };
}

async function saveData(entries, sha, message) {
  const octokit = getOctokit();
  const content = Buffer.from(
    JSON.stringify(entries, null, 2)
  ).toString("base64");
  await octokit.repos.createOrUpdateFileContents({
    owner: OWNER,
    repo: REPO,
    path: FILE_PATH,
    message: message || "Update data",
    content,
    sha,
    branch: BRANCH,
  });
}

module.exports = { getData, saveData };
