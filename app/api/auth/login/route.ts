import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    // For demo purposes, accepting any email/password combination
    if (!email || !password) {
      return NextResponse.json({ error: "Email and password are required" }, { status: 400 })
    }

    // Simulate user authentication
    const user = {
      id: "1",
      name: email.split("@")[0],
      email,
      role: "student",
    }

    // Create response with user data
    const response = NextResponse.json({
      success: true,
      user,
      message: "Login successful",
    })

    // Set authentication cookie (in production, use proper JWT tokens)
    response.cookies.set("auth-token", JSON.stringify(user), {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7 days
    })

    return response
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
