# MPU YouTube Title Generator

Internal tool for generating YouTube title suggestions based on MPU's performance data.

## Deploy to Railway (one-time, ~5 minutes)

### 1. Put the files on GitHub

1. Go to github.com → New repository
2. Name it `mpu-title-generator` → Create repository
3. Upload all files in this folder (main.py, requirements.txt, Procfile, and the static/ folder)

### 2. Deploy on Railway

1. Go to railway.app → Login with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `mpu-title-generator`
4. Railway will detect it automatically and start building

### 3. Add your environment variables

1. In Railway, click your project → **Variables** tab
2. Add these three variables:

| Name | Value |
|------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (get one at console.anthropic.com) |
| `SITE_USERNAME` | The login username — e.g. `mpu` |
| `SITE_PASSWORD` | The login password — choose something strong |

3. Railway will redeploy automatically

Anyone visiting the URL will see a browser login prompt before they can access anything.
Share the username and password with your team over Slack.

### 4. Get your URL

1. Click **Settings** → **Networking** → **Generate Domain**
2. You'll get a URL like `mpu-title-generator.up.railway.app`
3. Share that URL + the username/password with your team

## Usage

1. Open the URL in any browser
2. Enter the username and password when prompted
3. Upload a script (.docx or .txt)
4. Pick your metric and hit Generate

## Updating the password

Go to Railway → Variables → change `SITE_PASSWORD` → Railway redeploys in ~30 seconds.

## Updating performance data

The video performance data lives in `main.py` in the `TOP_VIDEOS` list.
To update it, edit that list and push to GitHub — Railway redeploys automatically.

## Cost

- Railway free tier: $5/month credit (usually enough for light internal use)
- Anthropic API: ~$0.01–0.03 per generation depending on script length
