import { type NextRequest, NextResponse } from "next/server"

// Python FastAPI server for chat with notes
const CHAT_SERVER_URL = process.env.CHAT_SERVER_URL || "http://localhost:8000"

async function retryWithBackoff(fn: () => Promise<Response>, maxRetries = 3): Promise<Response> {
  let lastError: Error | null = null

  for (let i = 0; i < maxRetries; i++) {
    try {
      console.log(`[v0] Chat API attempt ${i + 1}/${maxRetries}`)
      const response = await fn()

      console.log(`[v0] Response status: ${response.status}`)

      // Don't retry on client errors (4xx except 429) or success
      if (response.ok || (response.status >= 400 && response.status < 500 && response.status !== 429)) {
        return response
      }

      // Only retry on 429 (rate limit) or 5xx (server errors)
      if (response.status === 429 || response.status >= 500) {
        const waitTime = Math.pow(2, i) * 1000 + Math.random() * 1000
        console.log(`[v0] Retrying after ${waitTime}ms due to status ${response.status}`)
        await new Promise((resolve) => setTimeout(resolve, waitTime))
        continue
      }

      return response
    } catch (error) {
      console.log(`[v0] Network error on attempt ${i + 1}:`, error)
      lastError = error instanceof Error ? error : new Error(String(error))

      if (i === maxRetries - 1) {
        throw lastError
      }

      // Wait before retrying network errors
      const waitTime = Math.pow(2, i) * 1000 + Math.random() * 1000
      console.log(`[v0] Retrying after ${waitTime}ms due to network error`)
      await new Promise((resolve) => setTimeout(resolve, waitTime))
    }
  }

  throw lastError || new Error("Max retries exceeded")
}

export async function POST(request: NextRequest) {
  try {
    const { question, context, responseMode, use_pdf } = await request.json()

    if (!question) {
      return NextResponse.json({ error: "Question is required" }, { status: 400 })
    }

    console.log(`[Chat API] Forwarding request to Python server at ${CHAT_SERVER_URL}`)
    console.log(`[Chat API] use_pdf: ${use_pdf}`)

    // If use_pdf is true, use RAG system (PDF should already be uploaded and indexed)
    // If use_pdf is false, use general LLM with context from text files
    const useRAG = use_pdf === true
    
    // Build the message
    let message = question
    
    // Only add text file context if NOT using RAG (RAG uses PDF index)
    if (!useRAG && context && context.trim().length > 0) {
      message = `Context from uploaded study materials:\n${context}\n\nStudent Question: ${question}\n\nPlease answer the question based on the provided context. If the context doesn't contain relevant information, provide a general educational response.`
    }

    // Forward request to Python FastAPI server
    // Python expects: { message: str, use_pdf: bool }
    let response: Response
    try {
      // Add timeout to prevent hanging (2 minutes)
      const timeoutMs = 120000
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs)
      
      try {
        response = await retryWithBackoff(() =>
          fetch(`${CHAT_SERVER_URL}/chat`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              message: message,
              use_pdf: useRAG, // Use RAG if PDF is available
            }),
            signal: controller.signal,
          }),
        )
        clearTimeout(timeoutId)
      } catch (error) {
        clearTimeout(timeoutId)
        if (error instanceof Error && error.name === 'AbortError') {
          return NextResponse.json(
            {
              error: "Request timeout",
              details: "The chat server took too long to respond. Please try again with a simpler question or check if the server is processing a large PDF.",
            },
            { status: 504 }
          )
        }
        throw error
      }
    } catch (fetchError) {
      // If we can't connect to Python server, return helpful error
      console.error(`[Chat API] Cannot connect to Python server:`, fetchError)
      return NextResponse.json(
        {
          error: "Chat server is not available",
          details: "The Python chat server is not running. Please start it with: cd pp && python main_cn.py",
          suggestion: "Make sure Ollama is running and the Python server is started on port 8000"
        },
        { status: 503 }
      )
    }

    console.log(`[Chat API] Response status: ${response.status}`)

    if (!response.ok) {
      const errorData = await response.text()
      console.error(`[Chat API] Server error (${response.status}):`, errorData)

      if (response.status === 429) {
        return NextResponse.json(
          {
            error: "API quota exceeded. Please try again in a few minutes.",
            quotaInfo: "You've reached the free tier limits. The chat will be available again shortly.",
          },
          { status: 429 },
        )
      }

      if (response.status === 503) {
        return NextResponse.json(
          { error: "Chat service is unavailable. Please ensure the Python server is running on port 8000." },
          { status: 503 },
        )
      }

      return NextResponse.json(
        {
          error: `Chat service error (${response.status}). Please try again.`,
          details: errorData,
        },
        { status: response.status },
      )
    }

    const data = await response.json()

    // Check for errors in Python server response
    if (data.error) {
      console.error(`[Chat API] Python server error:`, data.error)
      // If RAG failed, fall back to general LLM with context
      if (useRAG && data.error.includes("PDF") || data.error.includes("FAISS")) {
        console.log(`[Chat API] RAG failed, falling back to general LLM with context`)
        // Retry with general LLM and context
        const fallbackMessage = context && context.trim().length > 0
          ? `Context from uploaded study materials:\n${context}\n\nStudent Question: ${question}\n\nPlease answer the question based on the provided context. If the context doesn't contain relevant information, provide a general educational response.`
          : question
        
        try {
          const fallbackResponse = await retryWithBackoff(() =>
            fetch(`${CHAT_SERVER_URL}/chat`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                message: fallbackMessage,
                use_pdf: false,
              }),
            }),
          )
          
          if (fallbackResponse.ok) {
            const fallbackData = await fallbackResponse.json()
            if (fallbackData.answer) {
              return NextResponse.json({ 
                answer: fallbackData.answer,
                warning: "PDF indexing unavailable, using general response"
              })
            }
          }
        } catch (fallbackError) {
          console.error(`[Chat API] Fallback also failed:`, fallbackError)
        }
      }
      
      return NextResponse.json(
        {
          error: data.error,
          details: data.details || "Please try again or upload the PDF again.",
        },
        { status: 500 }
      )
    }

    // Handle different response formats from Python server
    if (data.answer) {
      return NextResponse.json({ answer: data.answer })
    } else if (data.response) {
      return NextResponse.json({ answer: data.response })
    } else if (typeof data === "string") {
      return NextResponse.json({ answer: data })
    }

    return NextResponse.json({ answer: JSON.stringify(data) })
  } catch (error) {
    console.error("[v0] Chat API Error:", error)

    if (error instanceof Error) {
      if (error.message.includes("429") || error.message.includes("quota")) {
        return NextResponse.json(
          {
            error: "API quota exceeded. Please try again later.",
            quotaInfo: "The free tier has daily and per-minute limits.",
          },
          { status: 429 },
        )
      }

      if (error.message.includes("fetch") || error.message.includes("ECONNREFUSED")) {
        return NextResponse.json(
          { 
            error: "Cannot connect to chat server. Please ensure the Python server is running on port 8000.",
            details: "Start the server with: cd pp && python main_cn.py"
          },
          { status: 503 },
        )
      }
    }

    return NextResponse.json(
      {
        error: "Internal server error. Please try again.",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 },
    )
  }
}
