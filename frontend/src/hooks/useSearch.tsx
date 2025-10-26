import { createGoogleGenerativeAI } from "@ai-sdk/google"
import { generateText } from "ai"

const google = createGoogleGenerativeAI({
  apiKey: process.env.GOOGLE_API_KEY!,
})

export async function DiscoverAI(query: string) {
  const { sources } = await generateText({
    model: google("gemini-2.5-flash"),
    tools: {
      google_search: google.tools.googleSearch({}),
    },
    prompt: `List the top 5 results for "${query}". Only return the title, URL.`,
  })

  return (
    sources?.map((s: any) => ({
      public_id: s.id,
      title: s.title,
      url: s.url,
      format: s.sourceType,
      checked: true,
      created_at: new Date(),
      updated_at: new Date(),
    })) || []
  )
}
