// Front Panel Bridge - Scriptable Widget
// ホーム画面ウィジェットでPC電源状態を表示し、タップで操作

const BASE_URL = "http://elise-info.local:8080";

// --- API ---

async function getStatus() {
  try {
    const req = new Request(`${BASE_URL}/status`);
    req.timeoutInterval = 5;
    return await req.loadJSON();
  } catch {
    return null;
  }
}

async function postAction(path) {
  const req = new Request(`${BASE_URL}${path}`);
  req.method = "POST";
  req.timeoutInterval = 10;
  return await req.loadJSON();
}

// --- Widget ---

async function createWidget() {
  const status = await getStatus();
  const w = new ListWidget();
  w.backgroundColor = new Color("#1a1a2e");
  w.setPadding(12, 16, 12, 16);

  // Title
  const title = w.addText("Front Panel Bridge");
  title.font = Font.semiboldSystemFont(11);
  title.textColor = new Color("#888");
  w.addSpacer(8);

  if (!status) {
    const err = w.addText("接続できません");
    err.font = Font.mediumSystemFont(14);
    err.textColor = new Color("#f87171");
    w.addSpacer();
    return w;
  }

  // Power status
  const powerRow = w.addStack();
  powerRow.centerAlignContent();
  const powerDot = powerRow.addText("●");
  powerDot.font = Font.systemFont(18);
  powerDot.textColor = status.pc_power
    ? new Color("#4ade80")
    : new Color("#666");
  powerRow.addSpacer(8);
  const powerLabel = powerRow.addText(status.pc_power ? "ON" : "OFF");
  powerLabel.font = Font.boldSystemFont(20);
  powerLabel.textColor = Color.white();

  w.addSpacer(6);

  // HDD + Beep row
  const infoRow = w.addStack();
  infoRow.centerAlignContent();
  infoRow.spacing = 12;

  const hddDot = infoRow.addText("●");
  hddDot.font = Font.systemFont(10);
  hddDot.textColor = status.hdd_active
    ? new Color("#f59e0b")
    : new Color("#444");
  const hddLabel = infoRow.addText("HDD");
  hddLabel.font = Font.systemFont(10);
  hddLabel.textColor = new Color("#888");

  const beepDot = infoRow.addText("●");
  beepDot.font = Font.systemFont(10);
  beepDot.textColor = status.beep
    ? new Color("#f87171")
    : new Color("#444");
  const beepLabel = infoRow.addText("BEEP");
  beepLabel.font = Font.systemFont(10);
  beepLabel.textColor = new Color("#888");

  w.addSpacer();

  // Tap to toggle
  w.url = `${BASE_URL}/power/toggle`;

  return w;
}

// --- Main ---

if (config.runsInWidget) {
  const w = await createWidget();
  Script.setWidget(w);
} else if (args.queryParameters?.action) {
  // URLスキーム経由の操作
  const result = await postAction(`/${args.queryParameters.action}`);
  const n = new Notification();
  n.title = "Front Panel Bridge";
  n.body = JSON.stringify(result);
  await n.schedule();
} else {
  // アプリ内で実行 → ステータス表示
  const status = await getStatus();
  if (status) {
    const table = new UITable();
    const row = new UITableRow();
    row.addText(
      `電源: ${status.pc_power ? "ON" : "OFF"}`,
      `HDD: ${status.hdd_active ? "Active" : "Idle"} / Beep: ${status.beep ? "ON" : "OFF"}`
    );
    table.addRow(row);

    const actions = [
      ["Power Toggle", "/power/toggle"],
      ["Reset", "/reset"],
      ["Force OFF", "/power/off"],
    ];
    for (const [label, path] of actions) {
      const r = new UITableRow();
      const cell = r.addButton(label);
      cell.onTap = async () => {
        const res = await postAction(path);
        const a = new Alert();
        a.title = label;
        a.message = JSON.stringify(res);
        await a.present();
      };
      table.addRow(r);
    }
    await table.present();
  } else {
    const a = new Alert();
    a.title = "接続エラー";
    a.message = `${BASE_URL} に接続できません`;
    await a.present();
  }
}

Script.complete();
