import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const CORS = {
  "Access-Control-Allow-Origin":  "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, apikey",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }

  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405, headers: CORS });
  }

  const ANTHROPIC_KEY = Deno.env.get("ANTHROPIC_API_KEY");
  if (!ANTHROPIC_KEY) {
    return new Response(JSON.stringify({ error: "API key not configured" }),
      { status: 500, headers: { ...CORS, "Content-Type": "application/json" } });
  }

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }),
      { status: 400, headers: { ...CORS, "Content-Type": "application/json" } });
  }

  // Forward to Claude with streaming
  const claudeRes = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key":            ANTHROPIC_KEY,
      "anthropic-version":    "2023-06-01",
      "content-type":         "application/json",
    },
    body: JSON.stringify({ ...(body as object), stream: true }),
  });

  if (!claudeRes.ok) {
    const err = await claudeRes.text();
    return new Response(err, {
      status: claudeRes.status,
      headers: { ...CORS, "Content-Type": "application/json" }
    });
  }

  // Stream the response straight back to the browser
  return new Response(claudeRes.body, {
    status: 200,
    headers: {
      ...CORS,
      "Content-Type":      "text/event-stream",
      "Cache-Control":     "no-cache",
      "X-Accel-Buffering": "no",
    },
  });
});
