# RestrictedContentDL — How to Run (Any Laptop)

This guide covers setup, daily use, and safe shutdown/cleanup.

---

## 1) Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin)
- A Telegram **bot token**
- A Telegram **API ID** and **API HASH**
- A **SESSION_STRING** for your user account

---

## 2) First‑time setup

1) **Clone the repo**
```
git clone https://github.com/bisnuray/RestrictedContentDL
cd RestrictedContentDL
```

2) **Create or edit `config.env`**
Open `config.env` and replace the placeholders:

- `API_ID`
- `API_HASH`
- `BOT_TOKEN`
- `SESSION_STRING`

Optional tuning (recommended to avoid FloodWait):
```
MAX_CONCURRENT_DOWNLOADS=1
BATCH_SIZE=1
FLOOD_WAIT_DELAY=10
```

---

## 3) Start the bot

### Foreground (see logs in terminal)
```
docker compose up --build --remove-orphans
```

### Background (recommended)
```
docker compose up -d --build --remove-orphans
```

View logs:
```
docker compose logs -f
```

---

## 4) Use the bot (Telegram chat)

**Single post:**
```
/dl https://t.me/c/123456789/10
```

**Batch range:**
```
/bdl https://t.me/c/123456789/3 https://t.me/c/123456789/2598
```

**Stop current work:**
```
/killall
```

**Clean leftover temp files:**
```
/cleanup
```

**Stats / Logs:**
```
/stats
/logs
```

---

## 5) Stop the bot

```
docker compose down
```

---

## 6) Update the code

```
git pull
docker compose up -d --build --remove-orphans
```

---

## 7) Troubleshooting

### FloodWait / rate limits
Telegram will ask you to wait (e.g., “wait 2500 seconds”).

**What to do:**
- Stop the bot: `docker compose down`
- Wait out the cooldown
- Restart

**Prevent it:**
- Keep `MAX_CONCURRENT_DOWNLOADS=1`
- Keep `BATCH_SIZE=1`
- Keep `FLOOD_WAIT_DELAY=10`
- Run smaller ranges (e.g., 1–300, then 301–600)

---

## 8) Where files are stored

- Downloads are created **inside the container** at `downloads/`.
- Because the repo is mounted, these files appear on your laptop under:
  ```
  RestrictedContentDL/downloads/
  ```
- They are **usually deleted automatically** after upload.
- If leftovers remain, run `/cleanup`.

---

## 9) Quick restart checklist

1) `docker compose down`
2) `docker compose up -d --build --remove-orphans`
3) `docker compose logs -f`

