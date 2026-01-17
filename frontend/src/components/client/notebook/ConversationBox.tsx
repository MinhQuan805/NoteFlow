'use client'

// React hooks
import { useState, useEffect, useRef, useMemo, type FormEventHandler } from 'react'
import { useParams } from 'next/navigation'
import { Fragment } from 'react';
import { useChat } from '@ai-sdk/react';
import { UIMessage } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
// shadcn.io/ai components
import { Conversation, ConversationContent, ConversationScrollButton } from "@/components/ui/shadcn-io/ai/conversation"
import { Message, MessageContent } from "@/components/ui/shadcn-io/ai/message"
import { Response } from "@/components/ui/shadcn-io/ai/response"
import {
  PromptInput,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputToolbar,
} from '@/components/ui/shadcn-io/ai/prompt-input'
import {
  Source,
  Sources,
  SourcesContent,
  SourcesTrigger,
} from '@/components/ui/shadcn-io/ai/source';
import {
  Action,
  Actions
} from '@/components/ui/shadcn-io/ai/actions';
import { Reasoning, ReasoningContent, ReasoningTrigger } from '@/components/ui/shadcn-io/ai/reasoning';
import { Spinner } from '@/components/ui/shadcn-io/spinner/index';

// Icon
import { CopyIcon, Loader, RefreshCcwIcon, Presentation } from 'lucide-react';

// Packages
import axios from 'axios';
import * as z from 'zod';
import { toast } from 'react-toastify'

// Interface
import { MessageItem } from '@/schemas/conversation.interface'
import { updateTitle } from '@/lib/api/actionApi';

// Slide components
import SlidesViewer from './note/SlidesViewer';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

// Context for file filtering
import { useFileContext } from '@/contexts/FileContext';

export default function ConversationBox() {

  const params = useParams<{ notebookId: string; conversationId: string }>();
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [loading, setLoading] = useState(false)
  const [loadingQuery, setLoadingQuery] = useState<'submitted' | 'streaming' | 'ready' | 'error'>('ready');
  const [viewSlideHtml, setViewSlideHtml] = useState<string | null>(null);
  const [isSlideViewerOpen, setIsSlideViewerOpen] = useState(false);

  // Get file filter function from context
  const { getCheckedFileFilters } = useFileContext();

  // State to store all messages of the conversation
  const { messages, sendMessage, status, setMessages } = useChat({
    transport: new DefaultChatTransport({
      // api: '/api/chat',
      // // Include all chat messages + conversation ID for backend context
      // body: (messages: UIMessage[]) => ({
      //   messages,
      //   conversationId: params.conversationId,
      // }),
    }),
  });

  // Fetch conversation messages from API
  useEffect(() => {
    if (!params?.conversationId) return;

    const fetchData = async () => {
      try {
        if (params.conversationId) {
          setLoading(true)
          const conversationData = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/conversations/${params.conversationId}`)
          setMessages(conversationData.data.messages)
        }
      }
      finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [params.conversationId])

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Validation schema for user input using zod
  const schema = z.object({
    query: z.string().min(1, 'Please enter a query'),
  });

  const [text, setText] = useState('');

  // Handle form submission
  const handleSubmit: FormEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault();

    const result = schema.safeParse({ query: text });
    if (!result.success) {
      toast.error('Please enter a valid query');
      return;
    }

    // Create a new message object
    const newMessage: MessageItem = {
      id: crypto.randomUUID(),
      role: "user",
      parts: [{ type: "text", text: text }],
    };

    try {
      // Send the new message to API
      // const res = await axios.patch(
      //   `${process.env.NEXT_PUBLIC_API_URL}/conversations/${params.conversationId}`,
      //   newMessage,
      //   { headers: { 'Content-Type': 'application/json' } }
      // );

      // sendMessage({ text: text});
      const updatedMessages = [...messages, newMessage as any];
      setText('');
      setMessages(updatedMessages);
      if (updatedMessages.length < 2) {
        await updateTitle(`conversations/update_title/${params.conversationId}?title=${text.slice(0, 35)}...`);
      }
      setLoadingQuery('submitted');

      // Get checked file filters from context
      const fileFilters = getCheckedFileFilters();
      console.log('[ConversationBox] Sending query with file_filters:', fileFilters);

      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/query/${params.conversationId}`,
        {
          message_item: newMessage,
          query: text,
          file_filters: fileFilters.length > 0 ? fileFilters : null, // null = use all files
        },
        { headers: { 'Content-Type': 'application/json' } }
      );
      setLoadingQuery('ready');

      setMessages([...updatedMessages, res.data.response_message]);
    } catch (err) {
      console.error('Error posting:', err);
      toast.error('Cannot connect to server, please try again.');
    }
  };

  const handleViewSlide = (htmlContent: string) => {
    setViewSlideHtml(htmlContent);
    setIsSlideViewerOpen(true);
  };

  // Handle generate slides button click
  const handleGenerateSlides = async () => {
    // Use text if provided, otherwise use default prompt based on selected sources
    const fileFilters = getCheckedFileFilters();

    // Hard limit: exactly 1 document for slide generation
    if (fileFilters.length > 1) {
      toast.error('Please select exactly 1 document for slide generation');
      return;
    }

    const defaultTopic = fileFilters.length > 0
      ? `Create presentation slides from: ${fileFilters.join(', ')}`
      : 'Create presentation slides from the available documents';

    const topic = text.trim() ? text : defaultTopic;

    const newMessage: MessageItem = {
      id: crypto.randomUUID(),
      role: "user",
      parts: [{ type: "text", text: topic }],
    };

    try {
      const updatedMessages = [...messages, newMessage as any];
      setText('');
      setMessages(updatedMessages);
      setLoadingQuery('submitted');

      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/generate_slides/${params.conversationId}`,
        {
          message_item: newMessage,
          query: topic,
          file_filters: fileFilters.length > 0 ? fileFilters : null,
        },
        { headers: { 'Content-Type': 'application/json' } }
      );
      setLoadingQuery('ready');

      setMessages([...updatedMessages, res.data.response_message]);
      toast.success('Slides generated successfully!');
    } catch (err) {
      console.error('Error generating slides:', err);
      setLoadingQuery('ready');
      toast.error('Failed to generate slides. Please try again.');
    }
  };

  const renderedMessages = useMemo(() => {
    return messages.map((message) => (
      <div key={message.id}>
        {message.role === 'assistant' && message.parts.filter((part) => part.type === 'source-url').length > 0 && (
          <Sources>
            <SourcesTrigger
              count={
                message.parts.filter(
                  (part) => part.type === 'source-url',
                ).length
              }
            />
            {message.parts.filter((part) => part.type === 'source-url').map((part, i) => (
              <SourcesContent key={`${message.id}-${i}`}>
                <Source
                  key={`${message.id}-${i}`}
                  href={part.url}
                  title={part.url}
                />
              </SourcesContent>
            ))}
          </Sources>
        )}

        {message.parts.map((part, i) => {
          switch (part.type) {
            case 'text':
              return (
                <Fragment key={`${message.id}-${i}`}>
                  <Message className="max-w-full" from={message.role}>
                    <MessageContent>
                      {message.role === 'assistant' ? (
                        <Response>{part.text}</Response>
                      )
                        : (
                          <p className="whitespace-pre-wrap break-words">{part.text}</p>
                        )}
                    </MessageContent>
                  </Message>
                  {message.role === 'assistant' && i === messages.length - 1 && (
                    <Actions className="mt-2">
                      <Action
                        label="Retry"
                      >
                        <RefreshCcwIcon className="size-3" />
                      </Action>
                      <Action
                        onClick={() =>
                          navigator.clipboard.writeText(part.text)
                        }
                        label="Copy"
                      >
                        <CopyIcon className="size-3" />
                      </Action>
                    </Actions>
                  )}
                </Fragment>
              );
            case 'slides':
              return (
                <Fragment key={`${message.id}-${i}`}>
                  <div className="max-w-full mb-4">
                    <div className="border rounded-lg p-4 bg-gradient-to-r from-red-50 to-red-100">
                      <div className="flex items-center gap-2 mb-3">
                        <Presentation className="h-5 w-5 text-red-600" />
                        <h3 className="font-semibold text-gray-800">Presentation Slides Generated</h3>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        Your slides are ready to view!
                      </p>
                      <Button
                        onClick={() => handleViewSlide(part.text)}
                        className="bg-red-400 hover:bg-red-600 text-white rounded-full"
                      >
                        <Presentation className="h-4 w-4 mr-2" />
                        View Slides
                      </Button>
                    </div>
                  </div>
                </Fragment>
              );
            case 'reasoning':
              return (
                <Reasoning
                  key={`${message.id}-${i}`}
                  className="w-full"
                  isStreaming={status === 'streaming' && i === message.parts.length - 1 && message.id === messages.at(-1)?.id}
                >
                  <ReasoningTrigger />
                  <ReasoningContent>{part.text}</ReasoningContent>
                </Reasoning>
              );
            default:
              return null;
          }
        })}
      </div>
    ));
  }, [messages, status]);
  return (
    <div className="flex flex-col h-full w-full relative">
      {/* Conversation messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 pb-28">
        {loading ? (
          <div className="flex justify-center items-center h-full">
            <Spinner variant="ring" key="ring" />
          </div>
        ) : (
          <Conversation>
            <ConversationContent>
              {renderedMessages}
              {status === 'submitted' && <Loader />}
            </ConversationContent>
            <ConversationScrollButton />
            {loadingQuery === 'submitted' && (
              <div className="flex justify-start ml-6">
                <Spinner variant="ring" />
              </div>
            )}
            <div ref={messagesEndRef} />
          </Conversation>
        )}
      </div>

      {/* Fixed prompt input at the bottom */}
      <div className="p-2 border-t border-gray-200">
        <PromptInput onSubmit={handleSubmit} className="rounded-3xl">
          <PromptInputTextarea
            className='ml-1 mt-1'
            value={text}
            onChange={(e: any) => setText(e.target.value)}
            placeholder="Ask me anything..."
          />

          <PromptInputToolbar className='justify-end gap-2'>
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={handleGenerateSlides}
              disabled={loadingQuery === 'submitted' || getCheckedFileFilters().length > 1}
              className="rounded-full cursor-pointer h-8 w-8"
              title={getCheckedFileFilters().length > 1 ? 'Select only 1 document for slides' : 'Generate Slides'}
            >
              <Presentation className="h-4 w-4" />
            </Button>
            <PromptInputSubmit className='rounded-4xl mr-1 mb-1 cursor-pointer' status={loadingQuery} disabled={!text} />
          </PromptInputToolbar>
        </PromptInput>
      </div>

      {/* Slides Viewer Dialog */}
      <Dialog open={isSlideViewerOpen} onOpenChange={setIsSlideViewerOpen}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] p-0" showCloseButton={false}>
          {viewSlideHtml && (
            <SlidesViewer
              htmlContent={viewSlideHtml}
              onClose={() => setIsSlideViewerOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}