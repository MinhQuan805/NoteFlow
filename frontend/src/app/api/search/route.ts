import { NextResponse } from "next/server";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { generateText } from "ai";
import { v4 as uuidv4 } from 'uuid';

const google = createGoogleGenerativeAI({
  apiKey: process.env.GOOGLE_API_KEY!,
});

export async function POST(req: Request) {
  const body = await req.json();
  const query = body.query;

  if (!query) {
    return NextResponse.json(
      { error: "Missing 'query' in request body" },
      { status: 400 }
    );
  }

  try {
    const { text } = await generateText({
      model: google("gemini-2.5-flash"),
      tools: {
        google_search: google.tools.googleSearch({}),
      },
      prompt: `List the top 5 results for "${query}". 
              Return JSON format: { "url": "...", "title": "...", "description": "...", "format": "url", "checked": true }
              `,
    });
    let raw = text;
    raw = raw.replace(/^```json\s*/, '').replace(/\s*```$/, '');
    const data = JSON.parse(raw);
    const result = data.map((item: any) => ({
      ...item,
      public_id: uuidv4()
    }));
    console.log("AI Search Results:", result);
    return NextResponse.json(result);
  } catch (err) {
    console.error(err);
    return NextResponse.json(
      { error: "Failed to fetch AI search results" },
      { status: 500 }
    );
  }
}
