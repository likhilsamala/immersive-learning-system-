
import { type NextRequest, NextResponse } from "next/server"

// Python FastAPI server for create experiment
const EXPERIMENT_SERVER_URL = process.env.EXPERIMENT_SERVER_URL || "http://localhost:8001"

async function retryWithBackoff(fn: () => Promise<Response>, maxRetries = 3): Promise<Response> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fn()
      if (response.status !== 429) {
        return response
      }

      // If it's a 429, wait before retrying
      const waitTime = Math.pow(2, i) * 1000 + Math.random() * 1000 // Exponential backoff with jitter
      await new Promise((resolve) => setTimeout(resolve, waitTime))
    } catch (error) {
      if (i === maxRetries - 1) throw error
      // Wait before retrying on error
      const waitTime = Math.pow(2, i) * 1000 + Math.random() * 1000
      await new Promise((resolve) => setTimeout(resolve, waitTime))
    }
  }
  throw new Error("Max retries exceeded")
}

export async function POST(request: NextRequest) {
  try {
    const { title, description, files } = await request.json()

    if (!title && !description && (!files || files.length === 0)) {
      return NextResponse.json({ error: "Please provide a title, description, or files" }, { status: 400 })
    }

    console.log(`[Experiment API] Forwarding request to Python server at ${EXPERIMENT_SERVER_URL}`)

    // Build prompt from title, description, and files
    // Python expects: { prompt: str, template_hint?: str }
    // Combine title and description into a natural language prompt
    let prompt = ""
    
    if (title && description) {
      // If both are provided, create a comprehensive prompt
      prompt = `${title}. ${description}`
    } else if (title) {
      // If only title, use it as the main prompt
      prompt = title
      if (description) {
        prompt += `. ${description}`
      }
    } else if (description) {
      // If only description, use it as the prompt
      prompt = description
    }
    
    // Add files as additional context
    if (files && files.length > 0) {
      prompt += "\n\nAdditional context from uploaded files:\n"
      files.forEach((file: any) => {
        prompt += `File: ${file.name}\nType: ${file.type}\nContent: ${file.content || "[File content]"}\n\n`
      })
    }

    // Forward request to Python FastAPI server
    // Python endpoint is /generate, not /generate-experiment
    const response = await retryWithBackoff(() =>
      fetch(`${EXPERIMENT_SERVER_URL}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          template_hint: null, // Can be enhanced later
        }),
      }),
    )

    if (!response.ok) {
      const errorData = await response.text()
      console.error(`[Experiment API] Server error (${response.status}):`, errorData)

      if (response.status === 429) {
        return NextResponse.json(
          {
            error: "API quota exceeded. Please try again in a few minutes.",
            quotaInfo: "You've reached the free tier limits. Please try again later.",
          },
          { status: 429 },
        )
      }

      if (response.status === 503) {
        return NextResponse.json(
          { error: "Experiment service is unavailable. Please ensure the Python server is running on port 8001." },
          { status: 503 },
        )
      }

      return NextResponse.json({ error: "Failed to generate experiment" }, { status: response.status })
    }

    const pythonResponse = await response.json()

    // Python returns: { success: bool, config?: dict, html_code?: str, error?: str }
    // Frontend expects: { id, title, description, code, parameters, instructions }
    
    if (!pythonResponse.success) {
      return NextResponse.json(
        { error: pythonResponse.error || "Failed to generate experiment" },
        { status: 500 }
      )
    }

    // Transform Python response to frontend format
    const experimentData: any = {
      id: `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      title: title || pythonResponse.config?.title || "Custom Experiment",
      description: description || pythonResponse.config?.description || "AI-generated experiment",
      code: pythonResponse.html_code || "",
      parameters: [],
      instructions: [],
    }

    // Extract parameters from config if available
    if (pythonResponse.config) {
      // Try to extract parameters from config
      if (pythonResponse.config.parameters) {
        experimentData.parameters = pythonResponse.config.parameters
      } else if (pythonResponse.config.params) {
        // Convert params to parameters format
        experimentData.parameters = Object.entries(pythonResponse.config.params).map(([name, value]: [string, any]) => ({
          name,
          label: name.charAt(0).toUpperCase() + name.slice(1).replace(/_/g, " "),
          type: typeof value === "number" ? "number" : typeof value === "boolean" ? "boolean" : "select",
          default: value,
        }))
      }

      // Extract instructions if available
      if (pythonResponse.config.instructions) {
        experimentData.instructions = pythonResponse.config.instructions
      } else {
        experimentData.instructions = [
          "Review the generated experiment code",
          "Adjust parameters to see different behaviors",
          "Explore the interactive features",
        ]
      }
    } else {
      // Default parameters if no config
      experimentData.parameters = [
        {
          name: "speed",
          label: "Animation Speed",
          type: "number",
          min: 0.1,
          max: 5,
          default: 1,
          step: 0.1,
        },
      ]
      experimentData.instructions = [
        "Review the generated experiment",
        "Interact with the controls",
        "Observe the simulation behavior",
      ]
    }

    return NextResponse.json(experimentData)
  } catch (error) {
    console.error("Generate Experiment Error:", error)

    if (error instanceof Error && error.message.includes("429")) {
      return NextResponse.json(
        {
          error: "API quota exceeded. Please try again later.",
          quotaInfo: "The free tier has daily and per-minute limits. Try again in a few minutes.",
        },
        { status: 429 },
      )
    }

    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
