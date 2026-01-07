"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Users, Plus, LinkIcon, Clock, Video, Headphones } from "lucide-react"

interface ClassroomSession {
  id: string
  name: string
  host: string
  participants: number
  maxParticipants: number
  isVR: boolean
  createdAt: Date
}

export default function ClassroomPage() {
  const [roomName, setRoomName] = useState("")
  const [roomCode, setRoomCode] = useState("")
  const [activeSessions] = useState<ClassroomSession[]>([
    {
      id: "room-1",
      name: "Physics Study Group",
      host: "Dr. Smith",
      participants: 5,
      maxParticipants: 20,
      isVR: true,
      createdAt: new Date(Date.now() - 30 * 60 * 1000),
    },
    {
      id: "room-2",
      name: "Chemistry Lab Session",
      host: "Prof. Johnson",
      participants: 12,
      maxParticipants: 15,
      isVR: true,
      createdAt: new Date(Date.now() - 45 * 60 * 1000),
    },
    {
      id: "room-3",
      name: "Math Tutoring",
      host: "Ms. Davis",
      participants: 3,
      maxParticipants: 10,
      isVR: false,
      createdAt: new Date(Date.now() - 15 * 60 * 1000),
    },
  ])

  const createRoom = () => {
    if (!roomName.trim()) return
    // Generate room code and redirect to VR classroom
    const generatedCode = Math.random().toString(36).substring(2, 8).toUpperCase()
    window.location.href = `/classroom/room/${generatedCode}?name=${encodeURIComponent(roomName)}&host=true`
  }

  const joinRoom = () => {
    if (!roomCode.trim()) return
    window.location.href = `/classroom/room/${roomCode.toUpperCase()}`
  }

  const joinSession = (sessionId: string) => {
    window.location.href = `/classroom/room/${sessionId}`
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                ← Back
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <Users className="h-6 w-6 text-green-600" />
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">VR Classroom</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Create/Join Room */}
          <div className="lg:col-span-1 space-y-6">
            {/* Create Room */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  Create Classroom
                </CardTitle>
                <CardDescription>Start a new VR learning session</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="room-name">Room Name</Label>
                  <Input
                    id="room-name"
                    placeholder="Enter classroom name"
                    value={roomName}
                    onChange={(e) => setRoomName(e.target.value)}
                  />
                </div>
                <Button onClick={createRoom} className="w-full" disabled={!roomName.trim()}>
                  Create VR Room
                </Button>
              </CardContent>
            </Card>

            {/* Join Room */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LinkIcon className="h-5 w-5" />
                  Join Classroom
                </CardTitle>
                <CardDescription>Enter a room code to join</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="room-code">Room Code</Label>
                  <Input
                    id="room-code"
                    placeholder="Enter 6-digit code"
                    value={roomCode}
                    onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                    maxLength={6}
                  />
                </div>
                <Button
                  onClick={joinRoom}
                  variant="outline"
                  className="w-full bg-transparent"
                  disabled={!roomCode.trim()}
                >
                  Join Room
                </Button>
              </CardContent>
            </Card>

            {/* VR Requirements */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">VR Requirements</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Video className="h-4 w-4 text-blue-600" />
                  <span>WebXR compatible browser</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Headphones className="h-4 w-4 text-green-600" />
                  <span>VR headset (optional)</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Works on desktop, mobile, and VR headsets. VR mode provides the best immersive experience.
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Active Sessions */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Active Sessions</CardTitle>
                <CardDescription>Join ongoing classroom sessions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {activeSessions.map((session) => (
                    <div
                      key={session.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold">{session.name}</h3>
                          {session.isVR && <Badge variant="secondary">VR</Badge>}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
                          <span>Host: {session.host}</span>
                          <span className="flex items-center gap-1">
                            <Users className="h-4 w-4" />
                            {session.participants}/{session.maxParticipants}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            {Math.floor((Date.now() - session.createdAt.getTime()) / (1000 * 60))}m ago
                          </span>
                        </div>
                      </div>
                      <Button
                        onClick={() => joinSession(session.id)}
                        disabled={session.participants >= session.maxParticipants}
                      >
                        {session.participants >= session.maxParticipants ? "Full" : "Join"}
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
