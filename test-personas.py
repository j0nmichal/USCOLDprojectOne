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
        if f.get("pallet_positions"): obj["pallets"] = f["pallet_positions"]
        if tmin is not None and tmax is not None: obj["temp"] = f"{tmin}F to {tmax}F"
        if f.get("rail_access"):
            obj["rail"] = True
            if f.get("rail_carrier"): obj["rail_carrier"] = f["rail_carrier"]
        if caps:  obj["capabilities"]   = caps
        if certs: obj["certifications"] = certs
        data.append(obj)

    return f"""You are the US Cold virtual assistant. US Cold operates cold storage facilities across the United States.

YOUR ONLY JOB is to answer questions about US Cold's facilities — locations, capabilities, temperature ranges, pallet capacity, certifications, rail access, and contact information.

If anyone asks about anything unrelated to US Cold or cold storage, respond with exactly: "I'm here to help with questions about US Cold's cold storage facilities. What would you like to know?"

Rules:
- Be concise and direct. No filler phrases like "Great question!"
- Only state facts from the data below — never estimate or invent
- When asked for a phone number: immediately give the facility's phone field value. If it is null or empty, say "No phone number on file for that facility."
- When asked who to contact or for contact info: always give BOTH the warehouse contact AND the sales contact on separate lines, including name, phone, and email for each. If specific contacts are not set, give the general contact_email. Never deflect to "reach out through our website" or similar.
- When listing multiple facilities, use a clean list format
- Keep responses under 150 words unless a detailed comparison is asked for

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
        ]
    }
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
