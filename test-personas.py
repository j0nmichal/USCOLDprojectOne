#!/usr/bin/env python3
"""
US Cold Persona Tester
Run: python3 test-personas.py
Requires: ANTHROPIC_API_KEY in environment or set below.
"""

import os, json, textwrap, urllib.request, urllib.error, time

# ── Config ─────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://ypqeekmwqkafknajxuki.supabase.co"
SUPABASE_KEY = "sb_publishable_KZ6JO3EYjDCPkjzp8Ygs3A_iVQqFB81"
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-haiku-4-5-20251001"

# ── Fetch facilities ────────────────────────────────────────────────────────
def fetch_facilities():
    req = urllib.request.Request(
        SUPABASE_URL + "/rest/v1/facilities?select=*&order=name",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# ── Build system prompt (mirrors JS version exactly) ───────────────────────
def build_system_prompt(facilities):
    data = []
    for f in facilities:
        caps = [c for c, v in [
            ("Auto Quick Freeze" if f.get("quick_freeze_auto") else "Quick Freeze", f.get("quick_freeze")),
            ("Automated", f.get("automated")), ("Layer Pick", f.get("layer_pick")),
            ("Repack", f.get("repack")), ("Export/Import", f.get("export_import")),
            ("Organic", f.get("organic")), ("Dedicated", f.get("dedicated")),
        ] if v]
        certs = [c for c, v in [
            ("BRCGS", f.get("brcgs")), ("USDA", f.get("usda")),
            ("FDA", f.get("fda")), ("SQF", f.get("sqf")),
        ] if v]
        tmin, tmax = f.get("temp_min_f"), f.get("temp_max_f")
        obj = {"name": f.get("name"), "city": f.get("city"), "state": f.get("state")}
        if f.get("address"):       obj["address"] = f["address"]
        if f.get("zip"):           obj["zip"]     = f["zip"]
        if f.get("phone"):         obj["phone"]   = f["phone"]
        if f.get("contact_email"): obj["email"]   = f["contact_email"]
        if f.get("warehouse_contact_name"):
            obj["warehouse_contact"] = {k: v for k, v in {
                "name": f.get("warehouse_contact_name"),
                "email": f.get("warehouse_contact_email"),
                "phone": f.get("warehouse_contact_phone"),
            }.items() if v}
        if f.get("sales_contact_name"):
            obj["sales_contact"] = {k: v for k, v in {
                "name": f.get("sales_contact_name"),
                "email": f.get("sales_contact_email"),
                "phone": f.get("sales_contact_phone"),
            }.items() if v}
        if f.get("space_available") is not None: obj["space_available"] = f["space_available"]
        if f.get("pallet_positions"): obj["pallets"] = f["pallet_positions"]
        if tmin is not None and tmax is not None: obj["temp"] = f"{tmin}F to {tmax}F"
        if f.get("rail_access"):
            obj["rail"] = True
            if f.get("rail_carrier"): obj["rail_carrier"] = f["rail_carrier"]
        obj["brcgs"] = bool(f.get("brcgs"))
        if caps: obj["capabilities"] = caps
        other_certs = [c for c in certs if c != "BRCGS"]
        if other_certs: obj["certifications"] = other_certs
        data.append(obj)

    return f"""You are the US Cold virtual assistant. US Cold operates cold storage facilities across the United States.

YOUR ONLY JOB is to answer questions about US Cold's facilities — locations, capabilities, temperature ranges, pallet capacity, certifications, rail access, and contact information.

The guardrail redirect — respond with exactly "I'm here to help with questions about US Cold's cold storage facilities. What would you like to know?" — applies ONLY when the message contains NO facility names, NO facility abbreviations, NO cold storage terms (racks, pallets, temp, freeze, rail, cubes, slots, etc.), and NO US Cold related content.

If the message contains ANY of the following, ALWAYS answer it as a facility question — never redirect:
- A facility abbreviation: ARL, BAK, BTH, BTM, COV, DAL1, DAL2, DNT, DCC, FTW, FRE, HAR, HAZ, HEB, LAV, LKC, LR1, LR2, LR3, LEB, LUM, MCP, MCD1, MCD2, MIL, MIN, OMA, QTE, QTW, RVA, SMY, SYR, TRC, TLN, TLS, TKN, TKS, WAR, WIL
- A facility city or state name
- Cold storage terms: racks, racking, pallets, cubes, slots, temp, freeze, rail, space, storage, organic, automated, BRCGS, certified

Rules:
- Be concise and direct. No filler phrases like "Great question!"
- If the question asks for a single data point at a specific facility (racks, phone, address, temp range, availability, etc.) return ONLY the raw value and nothing else — no units, no labels, no extra context. Example: "racks MCD1" → "27,500" not "27,500 pallet positions". One answer, one line. Always format numbers with commas (40,000 not 40000).
- If asked for cubes/racks/pallets near a city (multiple facilities), sum the pallet positions of all nearby facilities and lead with the total, then list each facility's contribution.
- "Racks", "racking", "rack space", "slots", "cube", and "cubes" all mean pallet positions — answer accordingly
- Facility abbreviations — always resolve these to the correct facility:
  ARL=Arlington TX, BAK=Bakersfield CA, BTH=Bethlehem PA, BTM=Bethlehem Miller PA,
  COV=Covington TN, DAL1=Dallas South TX, DAL2=Dallas Halifax TX,
  DNT=Denton TX, DCC=Denton Cold Creek TX, FTW=Fort Worth TX, FRE=Fresno CA,
  HAR=Harrisonburg VA, HAZ=Hazleton PA, HEB=Hebron IN, LAV=La Vergne TN,
  LKC=Lake City FL, LR1=Laredo I TX, LR2=Laredo II TX, LR3=Laredo Island St TX,
  LEB=Lebanon IN, LUM=Lumberton NC, MCP=McClellan Park CA,
  MCD1=McDonough 1 GA, MCD2=McDonough 2 GA, MIL=Milford DE, MIN=Minooka IL,
  OMA=Omaha NE, QTE=Quakertown East PA, QTW=Quakertown West PA,
  RVA=Richmond VA, SMY=Smyrna TN, SYR=Syracuse UT, TRC=Tracy CA,
  TLN=Tulare North CA, TLS=Tulare South CA, TKN=Turlock North CA, TKS=Turlock South CA,
  WAR=Warsaw NC, WIL=Wilmington IL
- Only state facts from the data below — never estimate or invent
- When asked for a phone number: immediately give the facility's phone field value. If it is null or empty, say "No phone number on file for that facility."
- When asked who to contact or for contact info: always give BOTH the warehouse contact AND the sales contact on separate lines, including name, phone, and email for each. If specific contacts are not set, give the facility phone number. Never say "visit our website", "reach out through our website", or any variation — always give a direct phone number instead.
- For certifications and capabilities: only report what is explicitly in the data. The brcgs field is present on every facility as true or false — use it exactly.
- When listing multiple facilities near a location, put each on its own line in this format: "~X hours: Name, State — Front Desk: (phone)".
- Keep responses under 150 words unless a detailed comparison is asked for
- When asked if space is available at a facility: answer Yes if space_available is true, No if it is false. Do not hedge or say "contact us to check."
- When asked about pricing, rates, or how much space costs: say pricing varies by need and give the sales contact (name, phone, email). If no sales contact is on file, give the facility phone number.

FACILITY DATA:
{json.dumps(data, separators=(',', ':'))}"""

# ── Claude call ─────────────────────────────────────────────────────────────
def chat(system_prompt, messages):
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 512,
        "system": system_prompt,
        "messages": messages,
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["content"][0]["text"]

# ── Graders ─────────────────────────────────────────────────────────────────
def grade(response, checks):
    """
    checks: list of (description, callable(response) -> bool)
    Returns list of (description, passed, response_snippet)
    """
    results = []
    for desc, fn in checks:
        try:
            passed = fn(response)
        except Exception:
            passed = False
        results.append((desc, passed, response[:120].replace("\n", " ")))
    return results

# ── Personas ─────────────────────────────────────────────────────────────────

PERSONAS = {
    "US Cold Employee": {
        "description": "An internal US Cold employee verifying data accuracy and testing the tool they'd point customers to.",
        "turns": [
            {
                "message": "What's the address for the Fresno facility?",
                "checks": [
                    ("Returns a street address", lambda r: "East North" in r or "Avenue" in r or "Ave" in r),
                    ("Includes city/zip or zip code", lambda r: "93725" in r or "Fresno" in r),
                    ("No hallucinated address", lambda r: "2525" in r),
                ],
            },
            {
                "message": "Which facilities have rail access through Union Pacific?",
                "checks": [
                    ("Mentions at least 3 facilities", lambda r: sum(1 for x in ["Arlington","Bakersfield","Fresno","Laredo","Tulare","Tracy","McClellan"] if x in r) >= 3),
                    ("Names Union Pacific specifically", lambda r: "Union Pacific" in r or "UP" in r),
                    ("Uses list format", lambda r: "\n" in r or "-" in r or "•" in r),
                ],
            },
            {
                "message": "What's the phone number for Minooka?",
                "checks": [
                    ("Gives phone number directly", lambda r: "(815)" in r),
                    ("Does not deflect", lambda r: "website" not in r.lower() and "reach out" not in r.lower()),
                ],
            },
            {
                "message": "Who are the contacts at the Fort Worth facility?",
                "checks": [
                    ("Mentions warehouse contact", lambda r: "warehouse" in r.lower() or "No specific" in r or "not set" in r.lower() or "contact_email" in r.lower() or "on file" in r.lower()),
                    ("Mentions sales contact", lambda r: "sales" in r.lower() or "No specific" in r or "not set" in r.lower() or "on file" in r.lower()),
                    ("Does not say 'reach out through our website'", lambda r: "reach out through our website" not in r.lower()),
                ],
            },
            {
                "message": "How many pallet positions does McClellan have?",
                "checks": [
                    ("Gives a number", lambda r: any(c.isdigit() for c in r)),
                    ("Number is correct (83,148)", lambda r: "83" in r and "148" in r or "83148" in r),
                ],
            },
            {
                "message": "Which facilities offer organic storage?",
                "checks": [
                    ("Lists organic facilities", lambda r: any(x in r for x in ["Fresno","McClellan","Lumberton","Turlock"])),
                    ("Does not invent non-organic facilities", lambda r: "Arlington" not in r and "Minooka" not in r),
                ],
            },
            {
                "message": "What's the temperature range at the Covington TN facility?",
                "checks": [
                    ("Gives a temperature range", lambda r: "°F" in r or "-20" in r or "32" in r),
                    ("Correct range (-20 to 32)", lambda r: "-20" in r and "32" in r),
                ],
            },
            {
                "message": "Can you recommend a facility near Chicago with automation?",
                "checks": [
                    ("Suggests Minooka or Wilmington IL", lambda r: "Minooka" in r or "Wilmington" in r),
                    ("Mentions automation", lambda r: "automat" in r.lower()),
                ],
            },
            {
                "message": "Is space available at the Fresno facility?",
                "checks": [
                    ("Answers yes directly", lambda r: r.lower().startswith("yes") or "yes" in r.lower()[:40]),
                    ("Does not hedge or say contact us to check", lambda r: "contact us to check" not in r.lower() and "reach out" not in r.lower()),
                ],
            },
            {
                "message": "How much does storage cost there?",
                "checks": [
                    ("Acknowledges pricing varies", lambda r: "var" in r.lower() or "depend" in r.lower() or "pricing" in r.lower()),
                    ("Gives a phone number or mentions sales", lambda r: any(c.isdigit() for c in r) or "sales" in r.lower() or "contact" in r.lower()),
                    ("Does not give a made-up dollar amount", lambda r: "$" not in r and "per pallet" not in r.lower()),
                ],
            },
            {
                "message": "racks MCD1",
                "checks": [
                    ("Returns only the pallet count", lambda r: any(c.isdigit() for c in r)),
                    ("Does not include phone number or address", lambda r: "678" not in r and "Greenwood" not in r),
                    ("Response is short — one line", lambda r: len(r.strip().splitlines()) <= 2),
                ],
            },
        ]
    },

    "Logistics & Storage Manager": {
        "description": "A logistics manager evaluating US Cold facilities for a new distribution contract. Focused on location, capacity, rail, automation, and certs.",
        "turns": [
            {
                "message": "I need cold storage options in California close to major ports. What do you have?",
                "checks": [
                    ("Lists California facilities", lambda r: sum(1 for x in ["Bakersfield","Fresno","McClellan","Tracy","Tulare","Turlock"] if x in r) >= 2),
                    ("Mentions at least one city", lambda r: any(x in r for x in ["CA","California","Bakersfield","Fresno","Tracy","Turlock","Tulare","McClellan"])),
                    ("Does not hallucinate non-CA facilities", lambda r: "Ohio" not in r and "Texas" not in r),
                ],
            },
            {
                "message": "Which of those have Union Pacific rail access?",
                "checks": [
                    ("Names confirmed UP facilities in CA", lambda r: any(x in r for x in ["Bakersfield","Fresno","Tracy","Tulare"])),
                    ("Does not list Turlock (no UP carrier on file)", lambda r: "Turlock" not in r),
                ],
            },
            {
                "message": "I need at least 70,000 pallet positions. Which facilities can handle that?",
                "checks": [
                    ("Returns qualifying facilities", lambda r: any(x in r for x in ["Fresno","McClellan","Tulare"])),
                    ("Includes pallet counts", lambda r: any(c.isdigit() for c in r)),
                    ("Does not include sub-70k facilities", lambda r: "Harrisonburg" not in r and "Smyrna" not in r),
                ],
            },
            {
                "message": "Does McClellan have automated picking?",
                "checks": [
                    ("Confirms yes", lambda r: "yes" in r.lower() or "automat" in r.lower()),
                    ("Does not say no or unknown", lambda r: "does not" not in r.lower() and "no automat" not in r.lower()),
                ],
            },
            {
                "message": "What temperature range does McClellan support? I'm storing frozen seafood.",
                "checks": [
                    ("Gives temperature range", lambda r: "F" in r and any(c.isdigit() for c in r)),
                    ("Includes a sub-zero temp", lambda r: "-" in r),
                    ("Does not fabricate a range", lambda r: "-20" in r or "20" in r),
                ],
            },
            {
                "message": "Is space available there?",
                "checks": [
                    ("Answers yes or no directly", lambda r: "yes" in r.lower()[:60] or "no" in r.lower()[:30]),
                    ("Does not hedge", lambda r: "contact us to check" not in r.lower() and "reach out" not in r.lower()),
                ],
            },
            {
                "message": "Which facilities are BRCGS certified?",
                "checks": [
                    ("Confirms most/all facilities are BRCGS", lambda r: any(x in r.lower() for x in ["all", "most", "34", "certified"])),
                    ("Says no facilities are BRCGS certified", lambda r: "none" in r.lower() or "no facilities" in r.lower() or "not brcgs" in r.lower() or "0" in r or "aren't" in r.lower() or "are not" in r.lower()),
                ],
            },
            {
                "message": "How do I get a quote for McClellan?",
                "checks": [
                    ("Gives a phone number or contact", lambda r: any(c.isdigit() for c in r)),
                    ("Does not say visit our website", lambda r: "visit our website" not in r.lower()),
                    ("Routes to sales or facility contact", lambda r: "sales" in r.lower() or "contact" in r.lower() or "(" in r),
                ],
            },
        ]
    },

    "Off-Topic User": {
        "description": "A user who asks things outside US Cold's scope — competitors, general cold storage advice, weather, recipes, pricing sheets. Tests guardrail redirects.",
        "turns": [
            {
                "message": "What's the weather like in Chicago right now?",
                "checks": [
                    ("Redirects to US Cold topic", lambda r: "cold storage" in r.lower() or "facilities" in r.lower() or "us cold" in r.lower()),
                    ("Does not answer the weather question", lambda r: "°" not in r and "forecast" not in r.lower() and "sunny" not in r.lower()),
                ],
            },
            {
                "message": "How does US Cold compare to Lineage Logistics?",
                "checks": [
                    ("Does not compare or discuss competitor", lambda r: "lineage" not in r.lower() or "can't compare" in r.lower() or "don't have" in r.lower()),
                    ("Redirects to US Cold facilities", lambda r: "us cold" in r.lower() or "facilities" in r.lower() or "cold storage" in r.lower()),
                ],
            },
            {
                "message": "Can you help me write a cover letter for a job application?",
                "checks": [
                    ("Refuses and redirects", lambda r: "cover letter" not in r.lower() or "can't" in r.lower() or "here to help" in r.lower()),
                    ("Uses the exact redirect phrase or similar", lambda r: "cold storage" in r.lower() or "facilities" in r.lower()),
                ],
            },
            {
                "message": "What's the best way to freeze a turkey at home?",
                "checks": [
                    ("Does not give home freezing advice", lambda r: "wrap" not in r.lower() and "bag" not in r.lower() and "freezer burn" not in r.lower()),
                    ("Redirects to cold storage topic", lambda r: "cold storage" in r.lower() or "facilities" in r.lower()),
                ],
            },
            {
                "message": "OK fine. Do you have any facilities in Florida?",
                "checks": [
                    ("Returns to answering facility questions", lambda r: "florida" in r.lower() or "fl" in r or "lake city" in r.lower()),
                    ("Gives facility info", lambda r: any(c.isdigit() for c in r) or "lake city" in r.lower()),
                ],
            },
            {
                "message": "What are your competitor's prices?",
                "checks": [
                    ("Does not provide competitor pricing", lambda r: "$" not in r or "don't have" in r.lower() or "can't" in r.lower()),
                    ("Declines to discuss competitor pricing", lambda r: "can't" in r.lower() or "don't have" in r.lower() or "us cold" in r.lower() or "facilities" in r.lower()),
                ],
            },
            {
                "message": "Can you just give me a general list of all cold storage companies in the US?",
                "checks": [
                    ("Does not list competitors", lambda r: "lineage" not in r.lower() and "americold" not in r.lower() and "nichirei" not in r.lower()),
                    ("Redirects appropriately", lambda r: "us cold" in r.lower() or "cold storage" in r.lower() or "facilities" in r.lower()),
                ],
            },
        ]
    },
}

# ── Runner ───────────────────────────────────────────────────────────────────
PASS = "✅"
FAIL = "❌"
SEP  = "─" * 70

def run_persona(name, config, system_prompt):
    print(f"\n{'═'*70}")
    print(f"  PERSONA: {name}")
    print(f"  {config['description']}")
    print('═'*70)

    messages = []
    all_results = []

    for i, turn in enumerate(config["turns"], 1):
        msg = turn["message"]
        messages.append({"role": "user", "content": msg})

        print(f"\nTurn {i}: {msg}")
        print(SEP)

        try:
            response = chat(system_prompt, messages)
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 429:
                print("  [Rate limited — waiting 30s…]")
                time.sleep(30)
                try:
                    response = chat(system_prompt, messages)
                except urllib.error.HTTPError as e2:
                    response = f"[API ERROR {e2.code}: {e2.read().decode()}]"
            else:
                response = f"[API ERROR {e.code}: {body}]"

        # Pause between turns to stay under token-per-minute limit
        if i < len(config["turns"]):
            time.sleep(8)

        messages.append({"role": "assistant", "content": response})

        # Print wrapped response
        for line in textwrap.wrap(response, width=68):
            print(f"  {line}")

        # Grade
        results = grade(response, turn["checks"])
        all_results.extend(results)
        print()
        for desc, passed, _ in results:
            print(f"  {PASS if passed else FAIL}  {desc}")

    # Summary
    total  = len(all_results)
    passed = sum(1 for _, p, _ in all_results if p)
    failed = total - passed

    print(f"\n{SEP}")
    print(f"  SCORE: {passed}/{total} checks passed", end="")
    if failed:
        print(f"  ({failed} failed)")
        print(f"\n  Issues to review:")
        for desc, p, snippet in all_results:
            if not p:
                print(f"    {FAIL} {desc}")
                print(f"       Response: \"{snippet}...\"")
    else:
        print("  — all clear")
    print(SEP)

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not ANTHROPIC_KEY:
        print("ERROR: set ANTHROPIC_API_KEY environment variable before running.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        return

    print("Fetching facility data from Supabase...")
    facilities = fetch_facilities()
    print(f"Loaded {len(facilities)} facilities.")

    system_prompt = build_system_prompt(facilities)

    for persona_name, config in PERSONAS.items():
        run_persona(persona_name, config, system_prompt)

    print("\nDone.\n")

if __name__ == "__main__":
    main()
