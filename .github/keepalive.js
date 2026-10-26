// Opens the Streamlit app in a real browser so it counts as traffic. If the app is asleep,
// clicks the "get this app back up" button and waits for the app to load.
// Streamlit Community Cloud puts apps to sleep after 12 hours without traffic.
const { chromium } = require("playwright-core");

const url = process.env.APP_URL;
if (!url) { console.error("APP_URL is not set"); process.exit(1); }

(async () => {
  const browser = await chromium.launch({ executablePath: "/usr/bin/google-chrome", headless: true, args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(8000);

  const wake = page.getByRole("button", { name: /get this app back up/i });
  if (await wake.count()) {
    console.log("App was asleep. Clicking the wake-up button.");
    await wake.first().click();
  } else {
    console.log("App was already awake.");
  }

  // Awake means the Streamlit app container is on the page (main page or an iframe).
  const deadline = Date.now() + 180000;
  let awake = false;
  while (Date.now() < deadline && !awake) {
    for (const frame of page.frames()) {
      if (await frame.locator('[data-testid="stApp"]').count().catch(() => 0)) awake = true;
    }
    if (!awake) await page.waitForTimeout(5000);
  }
  await browser.close();

  if (!awake) { console.error("App did not load within 3 minutes."); process.exit(1); }
  console.log("App is awake:", url);
})();
