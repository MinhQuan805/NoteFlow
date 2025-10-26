import { streamText, UIMessage, convertToModelMessages } from 'ai';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { MessageItem } from '@/schemas/conversation.interface';
import axios from 'axios';

const google = createGoogleGenerativeAI({
  apiKey: process.env.GOOGLE_API_KEY!,
});

export async function POST(req: Request) {
  const { messages, conversationId }: { messages: UIMessage[]; conversationId: string } = await req.json();

  let fullText = '';

  const result = await streamText({
    model: google('gemini-2.5-flash'),
    messages: convertToModelMessages(messages),
    system: 'You are a helpful assistant that can answer questions and help with tasks',

    // Handle each chunk of text while the response is streaming
    onChunk: async (data) => {
      if (data.chunk.type === 'text-delta') {
        fullText += data.chunk.text; // Append partial text to the full message
      }
    },

    // Called when the streaming is finished
    onFinish: async () => {
      const assistantMessage: MessageItem = {
        id: crypto.randomUUID(),
        role: 'assistant',
        parts: [{ type: 'text', text: fullText }],
      };

      // Save the complete response to the database
      await axios.patch(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/${conversationId}`,
        assistantMessage,
        { headers: { 'Content-Type': 'application/json' } }
      );
    },
  });

  // Return the streaming response to show typing effect on the client
  return result.toUIMessageStreamResponse({
    sendReasoning: true,
  });
}
