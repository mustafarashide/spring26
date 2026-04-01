/*
FirstCity Bank - SQL Injection Training Lab
*/

const crypto = require("crypto");
const express = require("express");
const session = require("express-session");
const path = require("path");
const Database = require("better-sqlite3");

const app = express();
const PORT = 5001;

app.use(express.json());
app.use(session({ secret: "firstcity-bank-secret-2024", resave: false, saveUninitialized: false }));
app.use(express.static(__dirname));

const db = new Database(path.join(__dirname, "bank.db"));

function hashPassword(p) {
  return crypto.createHash("sha256").update(p).digest("hex");
}

function requireAuth(req, res, next) {
  if (!req.session.user_id) return res.status(401).json({ error: "Not authenticated" });
  next();
}

// =============================================================================
// ROUTES
// =============================================================================

// ── POST /api/login ───────────────────────────────────────────────────────────

app.post("/api/login", (req, res) => {
  const { username = "", password = "" } = req.body || {};
  const user = db
    .prepare("SELECT * FROM users WHERE username=? AND password_hash=?")
    .get(username, hashPassword(password));
  if (!user) return res.status(401).json({ error: "Invalid credentials" });
  req.session.user_id = user.id;
  req.session.username = user.username;
  return res.json({ username: user.username, full_name: user.full_name, account_number: user.account_number });
});

// ── POST /api/logout ──────────────────────────────────────────────────────────

app.post("/api/logout", (req, res) => { req.session.destroy(() => res.json({ ok: true })); });

// ── GET /api/me ───────────────────────────────────────────────────────────────

app.get("/api/me", requireAuth, (req, res) => {
  const user = db.prepare("SELECT * FROM users WHERE id=?").get(req.session.user_id);
  if (!user) return res.status(404).json({ error: "User not found" });
  return res.json({ username: user.username, full_name: user.full_name });
});

// ── GET /api/balance ──────────────────────────────────────────────────────────

app.get("/api/balance", requireAuth, (req, res) => {
  const acc = db
    .prepare("SELECT balance, account_type FROM accounts WHERE user_id=?")
    .get(req.session.user_id);
  return res.json({ balance: acc.balance, account_type: acc.account_type });
});

// ── POST /api/transfer ────────────────────────────────────────────────────────

app.post("/api/transfer", requireAuth, (req, res) => {
  const { to_account: toAccNum = "", amount: raw } = req.body || {};
  const amount = Number(raw ?? 0);
  if (!Number.isFinite(amount) || amount <= 0)
    return res.status(400).json({ error: "Invalid amount" });

  const sender = db.prepare("SELECT * FROM accounts WHERE user_id=?").get(req.session.user_id);
  const recpUser = db.prepare("SELECT * FROM users WHERE account_number=?").get(toAccNum);
  if (!recpUser) return res.status(404).json({ error: "Recipient not found" });
  if (sender.balance < amount) return res.status(400).json({ error: "Insufficient funds" });

  const recipient = db.prepare("SELECT * FROM accounts WHERE user_id=?").get(recpUser.id);

  db.transaction(() => {
    db.prepare("UPDATE accounts SET balance=balance-? WHERE id=?").run(amount, sender.id);
    db.prepare("UPDATE accounts SET balance=balance+? WHERE id=?").run(amount, recipient.id);
    db.prepare(
      "INSERT INTO transactions(from_account,to_account,amount,description) VALUES(?,?,?,?)"
    ).run(sender.id, recipient.id, amount, `Transfer to ${toAccNum}`);
  })();

  return res.json({ ok: true, new_balance: sender.balance - amount });
});

// ── GET /api/transactions ─────────────────────────────────────────────────────

app.get("/api/transactions", requireAuth, (req, res) => {
  const acc = db.prepare("SELECT id FROM accounts WHERE user_id=?").get(req.session.user_id);

  const allowedSort = new Set(["amount", "description", "created_at", "id"]);
  const sort = allowedSort.has(String(req.query.sort)) ? String(req.query.sort) : "created_at";
  const order = String(req.query.order || "DESC");
  const cols = String(req.query.cols || "id, amount, description, created_at");

  const query = `
    SELECT ${cols}
    FROM   transactions
    WHERE  from_account = ${acc.id} OR to_account = ${acc.id}
    ORDER  BY ${sort} ${order}
    LIMIT  50
  `;

  try {
    return res.json(db.prepare(query).all());
  } catch (_) {
    try {
      db.exec(query);
      return res.json({ ok: true });
    } catch (e) {
      return res.status(400).json({ error: e.message });
    }
  }
});

// ── GET /api/lookup ───────────────────────────────────────────────────────────

//TODO: this is vulnerable
app.get("/api/lookup", (req, res) => {
  const q = String(req.query.q || "");
  if (!q) return res.json([]);

  const query = `SELECT full_name, username FROM users WHERE full_name LIKE '%${q}%'`;

  try {
    return res.json(db.prepare(query).all());
  } catch (e) {
    return res.status(400).json({ error: e.message });
  }
});

// ── GET / ─────────────────────────────────────────────────────────────────────

app.get("/", (req, res) => res.sendFile(path.join(__dirname, "index.html")));

// =============================================================================

app.listen(PORT, () => console.log(`[+] FirstCity Bank on http://localhost:${PORT}`));
