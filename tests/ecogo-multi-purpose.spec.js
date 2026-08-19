const { test, expect } = require("@playwright/test");

function encodePolyline(points, precision = 5) {
  const factor = 10 ** precision;
  let lastLat = 0;
  let lastLon = 0;
  const out = [];
  const encode = (v) => {
    let value = v < 0 ? ~(v << 1) : v << 1;
    let str = "";
    while (value >= 0x20) {
      str += String.fromCharCode((0x20 | (value & 0x1f)) + 63);
      value >>= 5;
    }
    str += String.fromCharCode(value + 63);
    return str;
  };
  points.forEach((p) => {
    const lat = Math.round(p.lat * factor);
    const lon = Math.round(p.lon * factor);
    out.push(encode(lat - lastLat));
    out.push(encode(lon - lastLon));
    lastLat = lat;
    lastLon = lon;
  });
  return out.join("");
}

async function mockEcoGoNetwork(page) {
  await page.route("**/route", async (route) => {
    await route.fulfill({ status: 500, body: "valhalla-offline" });
  });

  await page.route("**/route/v1/driving/**", async (route) => {
    const points = [
      { lat: 25.0, lon: 121.0 },
      { lat: 25.03, lon: 121.03 },
      { lat: 25.08, lon: 121.08 },
      { lat: 25.12, lon: 121.12 },
      { lat: 25.18, lon: 121.18 },
      { lat: 25.22, lon: 121.22 },
    ];
    const geometry = encodePolyline(points, 5);
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        code: "Ok",
        routes: [{ geometry, distance: 80000, duration: 4200 }],
      }),
    });
  });

  await page.route("**/stations-ionex.json**", async (route) => {
    const stations = [];
    for (let i = 0; i < 1001; i += 1) {
      stations.push({
        id: `ionex-${i + 1}`,
        sourceId: `${i + 1}`,
        type: "station",
        operating_status: "opened",
        station_spec: "normal",
        lat: 24.0 + i * 0.0004,
        lon: 120.0 + i * 0.0004,
        gmap_name: `Ionex Mock ${i + 1}`,
        city: "台北市",
        district: "中正區",
        address: `中山路${i + 1}號`,
      });
    }
    stations[10].lat = 25.105;
    stations[10].lon = 121.105;
    stations[11].lat = 25.205;
    stations[11].lon = 121.205;
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        fetchedAt: "2026-08-19T00:00:00.000Z",
        source: "mock",
        stations,
      }),
    });
  });

  await page.route("**/location", async (route) => {
    await route.fulfill({ status: 500, body: "mock-live-disabled" });
  });

  await page.route("**/reverse?**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ features: [] }),
    });
  });
}

test("A→C 直達可規劃並安排站點", async ({ page }) => {
  await mockEcoGoNetwork(page);
  await page.goto("/");
  await page.fill("#start", "25.0000,121.0000");
  await page.fill("#end", "25.2000,121.2000");
  await page.keyboard.press("Escape");
  await page.locator("#end").blur();
  await page.click("#planBtn");

  await expect(page.locator("#resultCard")).toBeVisible();
  await expect(page.locator("#itinerary")).toContainText("終點");
  await expect(page.locator("#itinerary")).not.toContainText("停靠點 1");
  await expect(page.locator("#mStops")).not.toHaveText("0");
});

test("A→B→C 經停靠點可規劃並在終點附近安排站點", async ({ page }) => {
  await mockEcoGoNetwork(page);
  await page.goto("/");
  await page.fill("#start", "25.0000,121.0000");
  await page.click("#addViaBtn");
  await page.fill("#via-0", "25.1000,121.1000");
  await page.fill("#end", "25.2000,121.2000");

  await page.click("#planBtn");

  await expect(page.locator("#resultCard")).toBeVisible();
  await expect(page.locator("#itinerary")).toContainText("停靠點 1");
  await expect(page.locator("#itinerary")).toContainText("終點");
  await expect(page.locator("#itinerary")).toContainText("Ionex");
  await expect(page.locator("#mStops")).not.toHaveText("0");
});
