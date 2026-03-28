import os
import json
import secrets
import httpx
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

SITE_USERNAME = os.environ.get("SITE_USERNAME", "mpu")
SITE_PASSWORD = os.environ.get("SITE_PASSWORD", "")

def require_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not SITE_PASSWORD:
        return  # No password set — open access (shouldn't happen in prod)
    valid_user = secrets.compare_digest(credentials.username.encode(), SITE_USERNAME.encode())
    valid_pass = secrets.compare_digest(credentials.password.encode(), SITE_PASSWORD.encode())
    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

class GenerateRequest(BaseModel):
    script_text: str
    metric: str = "views"
    count: int = 5
    scope: str = "universal"

TOP_VIDEOS = [
    ("I Took Bernie Into Deep Trump Country. Can He Win Them Over?", 10594596, 3.38),
    ("What Dollar General Doesn't Want You To Know", 7614450, 6.39),
    ("BlackRock: The Conspiracies You Don't Know", 7552020, 3.98),
    ("How John Deere Robs Farmers Of $4 Billion A Year", 7409503, 3.44),
    ("It's Not Just Shein: Why Are ALL Your Clothes Worse Now?", 5900288, 2.92),
    ("We Put 7 Uber Drivers in One Room. What We Found Will Shock You.", 5689244, 6.28),
    ("How Corporations Are Secretly Poisoning Our Food Supply", 4789547, 5.81),
    ("We Went to Arkansas. The Farm Crisis Will Shock You", 4726325, 3.80),
    ("I Tracked Down The Company Ruining Restaurants", 4587056, 4.55),
    ("We Went to the Town Elon Musk Is Poisoning", 3809449, 4.15),
    ("What Sam Altman Doesn't Want You To Know", 3800792, 3.44),
    ("Private Equity's Ruthless Takeover Of The Last Affordable Housing In America", 3787326, 4.22),
    ("We Had 400 People Shop For Groceries. What We Found Will Shock You.", 3703035, 3.51),
    ("We Chased Driverless Trucks In Texas. What We Saw Will Scare You.", 3624901, 6.83),
    ("Why Vegas Doesn't Care If You Visit Anymore", 3567295, 5.56),
    ("How Stellantis Destroyed Jeep", 3549688, 3.13),
    ("The Lie That Made Food Conglomerates Rich...And Is Slowly Poisoning Us", 3527613, 4.46),
    ("I Worked At Palantir: The Tech Company Reshaping Reality", 3497689, 4.23),
    ("How Vail Destroyed Skiing", 3466418, 4.61),
    ("I Live 500 Feet From A Bitcoin Mine. My Life Is Hell.", 3421846, 6.34),
    ("Subscriptions Are Ruining Our Lives. Here's Why They're Everywhere Now.", 3165982, 3.39),
    ("I Live 400 Yards From Mark Zuckerberg's Massive Data Center", 3155781, 7.21),
    ("Tech Billionaires' Shocking Plot for Rural America", 3124083, 3.80),
    ("What the Maker of Ozempic Doesn't Want You to Know: It's Bankrupting America", 3017805, 5.25),
    ("How Tyson Captured All The Pork You Eat (And Made Billions)", 2919931, 5.15),
    ("OpenAl Showed Up At My Door. Here's Why They're Targeting People Like Me", 2873334, 4.64),
    ("We Went To Montana: The Housing Inequality Will Shock You", 2788498, 5.05),
    ("Trump Says He Will Save American Jobs. John Deere Is Calling His Bluff.", 2749513, 6.67),
    ("We Uncovered the Scheme Keeping Grocery Prices High", 2486977, 4.43),
    ("We Uncovered the Illegal Scam Happening at Every Stadium", 2159615, 6.39),
    ("We Found Corporate America's Biggest Enemy", 2154302, 5.46),
    ("What Ticketmaster Doesn't Want You To Know: Concerts Were Cheap For Decades", 2134390, 4.09),
    ("We Investigated Hundreds of Trump Donors: What We Found Will Shock You", 2115032, 4.76),
    ("Could Texas Run Out Of Water? Wall Street Is Betting Big On It.", 2060153, 2.36),
    ("Plastic Makers Have A Big Secret: They're Experimenting On You", 2038230, 5.08),
    ("The BlackRock Situation Just Got Worse...", 2007692, 4.51),
    ("We Went To Nebraska: The Beef Crisis Will Shock You", 1992607, 5.51),
    ("This Billionaire Family is Suffocating Rural America", 1910201, 6.83),
    ("McKinsey: The Group Secretly Running Every Company (And Government?)", 1872685, 5.23),
    ("I Worked At A Google Data Center: What I Saw Will Shock You.", 1857669, 5.58),
    ("Who Do Trump Voters Blame For America's Problems? It's Not Who You Think", 1831914, 5.36),
    ("The Secret Plan Behind Artificial Intelligence", 1827938, 3.90),
    ("The Lie So Dangerous Tesla Engineers Are Quitting", 1801797, 3.48),
    ("The People Breaking Immigration Law Are Not Who You Think", 1798919, 6.76),
    ("MEDIA BLACKOUT: America's Poorest Counties Devastated By Catastrophic Flooding", 1768525, 6.65),
    ("We Uncovered The Most Infamous Secret Society: And The Truth Is Shocking", 1718760, 6.05),
    ("The Untold Story of Alabama's Incarcerated Workers", 1704821, 6.44),
    ("Elliott County Voted for Democrats For 144 Years. Then Came Trump…", 1693808, 5.54),
    ("Italy's Radical Solution to Extreme Inequality", 1683513, 5.16),
    ("We Found the Most Corrupt Stock Traders", 1679744, 3.81),
    ("Billionaires Found a New Way to Steal Your Paycheck", 1592793, 3.93),
    ("The $1 Trillion Private Health Insurance Scam", 1590022, 5.55),
    ("How A Billionaire Scammed Buffalo Bills Fans", 1534000, 4.33),
    ("Why Starbucks Sucks Now", 1511663, 4.76),
    ("We Found The Radical Solution To Skyrocketing Grocery Prices", 1509327, 6.28),
    ("TSA Officers Have a Dire Warning for America", 1501712, 8.16),
    ("How Saudi Arabia Bought Trump - And What They Want", 1498827, 4.72),
    ("We Went To Florida: The Housing Insurance Crisis Will Shock You", 1478595, 4.10),
    ("We Investigated The Criminals Who Bought Trump: What We Found Will Shock You", 1453258, 5.94),
    ("Tech Billionaires' Shocking Plan For West Virginia", 1425876, 3.90),
    ("How the Big Beautiful Bill Will Transfer Trillions From Workers to Wall Street", 1424559, 4.54),
    ("The Most Corrupt Corporation in the World Is Taking Over Our Food Supply", 1404093, 6.22),
    ("Trump Promised American Jobs. Why Are These Truck Jobs Going To Mexico?", 1376698, 5.25),
    ("We Went To A Bernie Rally. We Didn't Find Who You'd Expect.", 1363172, 6.46),
    ("I Tracked Down The Companies Bribing Trump", 1334638, 5.10),
    ("What Capital One Doesn't Want You To Know", 1326327, 4.50),
]

def get_top_videos(metric: str, n: int):
    videos = [{"title": t, "views": v, "ctr": c} for t, v, c in TOP_VIDEOS]
    if metric == "views":
        return sorted(videos, key=lambda x: -x["views"])[:n]
    elif metric == "ctr":
        filtered = [v for v in videos if v["views"] > 500000]
        return sorted(filtered, key=lambda x: -x["ctr"])[:n]
    else:
        max_v = max(v["views"] for v in videos)
        max_c = max(v["ctr"] for v in videos)
        for v in videos:
            v["score"] = (v["views"] / max_v) * 0.6 + (v["ctr"] / max_c) * 0.4
        return sorted(videos, key=lambda x: -x["score"])[:n]

@app.post("/generate")
async def generate(req: GenerateRequest, _: None = Depends(require_auth)):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")

    tops = get_top_videos(req.metric, 25)
    metric_label = {"views": "total views", "ctr": "click-through rate", "combined": "combined views + CTR"}.get(req.metric, "total views")
    top_titles = "\n".join([f'{i+1}. "{v["title"]}" — {v["views"]/1000000:.1f}M views, {v["ctr"]}% CTR' for i, v in enumerate(tops)])

    scope_instruction = (
        "Prioritize titles that resonate with viewers who have NO prior knowledge of the specific topic — maximize reach beyond the core audience."
        if req.scope == "universal"
        else "Titles can assume some familiarity with the subject matter."
    )

    prompt = f"""You are a YouTube title strategist for More Perfect Union (MPU), a nonprofit video journalism outlet covering working-class economic issues and corporate accountability.

First, do a thorough analysis of what drives high performance in MPU's top videos — look at psychological triggers, emotional entry points, structural patterns, topic categories, what the viewer is promised, and how the best titles differ from generic YouTube titles. Use that analysis to generate {req.count} genuinely fresh title options for the script below. Do NOT simply plug the script's subject into existing title templates.

MPU's top-performing titles ranked by {metric_label}:
{top_titles}

Here is the video script:
---
{req.script_text[:9000]}
---

Scope instruction: {scope_instruction}

For each title:
1. Write the title
2. Write 2 sentences explaining the specific strategic insight — what psychological or structural principle it's built on, and why that fits this particular script
3. Write a 3-5 word strategy tag

Also include a 2-3 sentence "script_analysis" identifying the key emotional and strategic opportunities in this script for titling purposes.

Respond ONLY as JSON, no markdown, no preamble:
{{
  "script_analysis": "...",
  "titles": [
    {{ "title": "...", "reasoning": "...", "strategy_tag": "..." }}
  ]
}}"""

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}],
            },
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    clean = text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(clean)
    except Exception:
        import re
        m = re.search(r'\{[\s\S]*\}', clean)
        if m:
            parsed = json.loads(m.group())
        else:
            raise HTTPException(status_code=500, detail="Could not parse Claude response")

    return parsed

SHORTS_VIDEOS = [
    ("What Zuckerberg Doesn't Want You to See", 8970318, 7.8),
    ("Kristi Noem used our tax dollars as a personal bank for her friends", 5757876, 7.05),
    ("Peter Thiel Doesn't Want You to See This Clip", 4853806, 6.09),
    ("The Epstein Crimes You Haven't Heard About, Part 1", 3752045, 6.7),
    ("Why Bitcoin Could Hit $0", 3619843, 5.92),
    ("What Jeff Bezos Doesn't Want You to Know", 3554607, 8.97),
    ("The Billionaire Oligarchs Pushing For War With Iran", 3460505, 8.25),
    ("How Larry Ellison got so rich", 3027507, 6.96),
    ("Zohran Mamdani's radical plan to clear NYC's streets", 3009068, 8.33),
    ("Hot Mic Catches Zuckerberg Kneeling to Trump", 2679203, 5.98),
    ("John Deere is Making Life Miserable For Farmers — And Costing Many Their Lives", 2572146, 8.91),
    ("What the Epstein emails say about Bernie Sanders", 2500698, 8.5),
    ("Joann's is Closing in May. You Can Blame Private Equity", 2458099, 7.22),
    ("This Meta data center is the size of Manhattan. It could bankrupt Louisiana farmers.", 2416290, 7.45),
    ("U.S. Senator attacks anti-war Marine - breaking his hand", 2082104, 11.29),
    ("What Larry Ellison Doesn't Want You to Know", 2058503, 6.95),
    ("Their landlord abandoned them, then jacked up the rent. Now they're fighting back.", 2057600, 9.35),
    ("Tech Billionaires Have Found a NEW Way to Extort You", 1947659, 8.28),
    ("Trump is Using DoorDash to Gaslight You About Grocery Prices", 1935339, 9.33),
    ("Corporations have found a NEW way to rip you off", 1816892, 8.32),
    ("Marc Andreessen Doesn't Want You to See This", 1793993, 8.65),
    ("How Dollar General Is Secretly Robbing Its Customers", 1760305, 8.21),
    ("What DoorDash Doesn't Want You To Know", 1445343, 8.81),
    ("Half this town was just laid off. It's going to be a ghost town.", 1329858, 7.9),
    ("What Airlines Don't Want You to Know", 1326001, 8.29),
    ("What Life is REALLY Like Next to Zuckerberg's Manhattan-Sized Data Center", 1258206, 9.1),
    ("We Found Private Equity's Latest Target", 1214546, 7.1),
    ("What Trump's Tariffs Are REALLY About", 1110526, 7.43),
    ("The REAL Freeloaders in America Are Not Who You Think", 1100140, 7.67),
    ("What Elon Musk Doesn't Want You to Know", 1054439, 12.0),
    ("Corporations have found a NEW WAY to rip you off", 1004326, 8.66),
    ("Elon Musk is poisoning ANOTHER city. It's torture to be outside.", 915471, 8.27),
    ("Landlords freak out after committee votes for renter protections", 905671, 9.4),
    ("The REAL reason Trump is attacking public transit", 801907, 8.45),
    ("Why Wall Street Execs Are Losing Their Minds", 799136, 8.24),
    ("This Billionaire Couple Stole California's Water Supply", 764828, 7.7),
    ("What Republicans Don't Want You to Know About Their Stock Trading Ban", 760940, 8.47),
    ("We found the hidden reason Iran war propaganda is everywhere", 735969, 8.33),
    ("The REAL Reason Trump Wants to Take Greenland Next", 730632, 7.81),
    ("Twin Cities SHUT DOWN in historic general strike against ICE", 711972, 8.41),
    ("Trump Says He's Bailing Out Farmers. Here's Who REALLY Benefits", 690710, 7.85),
    ("Why the Real Estate Lobby is Terrified of Mayor Mamdani", 674322, 8.16),
    ("Trump is using a Walmart promotion to gaslight you about Thanksgiving prices", 631796, 7.92),
    ("Economic Blackout Spreads From Coast to Coast", 597312, 8.25),
    ("The secret, steroid-fueled group running the GOP", 587244, 7.44),
    ("Apple Tried to Stop Jon Stewart from Interviewing Lina Khan", 574963, 7.37),
    ("Argentinians have a dire warning for America", 512180, 8.2),
    ("ICE Raided Their Apartment Building. Instead of Scattering, Tenants Are Organizing.", 479980, 8.53),
    ("Trump Said He Would Save American Jobs. So Why Is This Iowa Auto Factory Closing?", 478988, 8.96),
    ("The First U.S. General Strike In 80 Years Is Happening Now In Minnesota", 471124, 9.43),
    ("Striking Baristas SHUT DOWN The Largest Starbucks Distribution Center In The World", 469458, 8.64),
    ("We Found the Hidden Reason Car Insurance Rates Have Skyrocketed", 473442, 7.51),
    ("Tyson Foods Is Laying Off 30% Of This Nebraska Town", 451434, 7.74),
    ("The TRUE cost of your Amazon deliveries", 445503, 7.67),
    ("You Need to Know This About Prime Day Deals", 470842, 8.68),
]

def get_top_shorts(metric: str, n: int):
    videos = [{"title": t, "views": v, "ctr": c} for t, v, c in SHORTS_VIDEOS]
    if metric == "views":
        return sorted(videos, key=lambda x: -x["views"])[:n]
    elif metric == "ctr":
        return sorted(videos, key=lambda x: -x["ctr"])[:n]
    else:
        max_v = max(v["views"] for v in videos)
        max_c = max(v["ctr"] for v in videos)
        for v in videos:
            v["score"] = (v["views"] / max_v) * 0.6 + (v["ctr"] / max_c) * 0.4
        return sorted(videos, key=lambda x: -x["score"])[:n]

@app.post("/generate-shorts")
async def generate_shorts(req: GenerateRequest, _: None = Depends(require_auth)):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")

    tops = get_top_shorts(req.metric, 25)
    metric_label = {"views": "total views", "ctr": "click-through rate", "combined": "combined views + CTR"}.get(req.metric, "total views")
    top_titles = "\n".join([f'{i+1}. "{v["title"]}" — {v["views"]/1000000:.1f}M views, {v["ctr"]}% CTR' for i, v in enumerate(tops)])

    scope_instruction = (
        "Prioritize titles that work for viewers with NO prior knowledge of the specific story — maximize scroll-stopping power on a general feed."
        if req.scope == "universal"
        else "Titles can assume some familiarity with the specific story or subject."
    )

    prompt = f"""You are a YouTube Shorts title strategist for More Perfect Union (MPU), a nonprofit video journalism outlet covering working-class economic issues and corporate accountability.

YouTube Shorts titles must work in under 2 seconds on a scrolling feed. They are fundamentally different from long-form titles:
- Urgency and present-tense action matter more than nuance
- Named villains (Zuckerberg, Bezos, Musk, a specific company) outperform category villains
- "REAL," "NEW," "Doesn't Want You to Know/See," "Gaslight," specific dollar amounts and vivid verbs all perform well
- Keep titles under 70 characters where possible — this is a hard YouTube recommendation for Shorts
- Lowercase or sentence case often feels more native to Shorts than Title Case

Analyze what drives high performance in MPU's top Shorts — psychological triggers, emotional entry points, structural patterns, the role of named villains vs. systemic framing, urgency signals, and character count discipline. Then use that analysis to generate {req.count} genuinely fresh title options for the content below. Do NOT simply slot the subject into existing templates.

MPU's top-performing Shorts ranked by {metric_label}:
{top_titles}

Here is the content/script:
---
{req.script_text[:6000]}
---

Scope instruction: {scope_instruction}

For each title:
1. Write the title
2. Write 2 sentences explaining the specific strategic insight — what psychological or structural principle makes this work for Shorts specifically
3. Write a 3-5 word strategy tag

Also include a 2-3 sentence "script_analysis" identifying the key hook, villain, and emotional trigger opportunities in this content for Shorts titling.

Respond ONLY as JSON, no markdown, no preamble:
{{
  "script_analysis": "...",
  "titles": [
    {{ "title": "...", "reasoning": "...", "strategy_tag": "..." }}
  ]
}}"""

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}],
            },
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    clean = text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(clean)
    except Exception:
        import re
        m = re.search(r'\{[\s\S]*\}', clean)
        if m:
            parsed = json.loads(m.group())
        else:
            raise HTTPException(status_code=500, detail="Could not parse response")

    return parsed


class ChatRequest(BaseModel):
    messages: list

@app.post("/chat")
async def chat(req: ChatRequest, _: None = Depends(require_auth)):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": req.messages,
            },
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    reply = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return {"reply": reply}


# Serve frontend with auth
@app.get("/")
async def serve_index(_: None = Depends(require_auth)):
    return FileResponse("static/index.html")

@app.get("/{path:path}")
async def serve_static(path: str, _: None = Depends(require_auth)):
    file_path = f"static/{path}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse("static/index.html")
