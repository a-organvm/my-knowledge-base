# Walking Through Remote Sharing

This guide explains how to share a "Whistleblower" link remotely using **ngrok** and the unified tunnel setup I've configured for you.

## 1. Unified Tunnel Setup

Instead of managing multiple tunnels, I've created a custom `ngrok_app.yml` that handles both the API and Web services.

**To start the tunnels and the application:**
```bash
# 1. Start Docker services
make docker-up

# 2. Start the unified ngrok tunnel
ngrok start --config ngrok_app.yml --all

# 3. Start the application services (in a separate terminal)
make dev
```

## 2. Remote Access URLs

The application is currently configured to use the following public URL for **both** the API and the Web Dashboard:

> **Public URL**: `https://symbolistical-amiya-mitigable.ngrok-free.dev`

- **Web Dashboard**: `https://symbolistical-amiya-mitigable.ngrok-free.dev` (Proxies to `localhost:3001`)
- **API (Swagger)**: `https://symbolistical-amiya-mitigable.ngrok-free.dev/api/docs` (Proxies to `localhost:3000`)

## 3. Creating and Sharing a Link

1. Open the Styx Mobile App.
2. Ensure the mobile app is pointing to the public URL (this is already set in your `.env` as `STYX_API_PUBLIC_URL`).
3. **Create a "No Contact" Contract**:
   - Fill in the details and submit.
   - The app will generate a unique whistleblower link.
4. **Copy the link**: It will look like `https://symbolistical-amiya-mitigable.ngrok-free.dev/whistleblower/{uuid}`.
5. **Share it**: Send this link to anyone. They will be able to submit evidence without being on your local network.

## 4. Default Login Credentials

Use these credentials to log in to the app or dashboard:

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@styx.protocol` | `demo-password-123` |
| **User** | `demo@styx.protocol` | `demo-password-123` |

---

### Troubleshooting
- **ngrok Warning**: You may see a "Deceptive site" or "Warning" page from ngrok. This is standard for free-tier tunnels. Click **"Visit Site"** to proceed.
- **Port Conflict**: The API runs on `3000` and the Web Dashboard on `3001`. The tunnels handle the routing automatically.
