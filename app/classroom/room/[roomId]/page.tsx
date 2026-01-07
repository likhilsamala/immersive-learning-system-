"use client"

import { useEffect, useState, useRef } from "react"
import { useParams, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { VRClassroom } from "@/components/vr/vr-classroom"
import { ParticipantsList } from "@/components/vr/participants-list"
import { VirtualWhiteboard } from "@/components/vr/virtual-whiteboard"
import {
  Users,
  Mic,
  MicOff,
  Video,
  VideoOff,
  Share,
  Settings,
  DoorClosedIcon as ExitIcon,
  Headphones,
  Monitor,
} from "lucide-react"

interface Participant {
  id: string
  name: string
  isHost: boolean
  isMuted: boolean
  isVideoOn: boolean
  avatar: {
    position: [number, number, number]
    rotation: [number, number, number]
  }
}

export default function VRClassroomRoom() {
  const params = useParams()
  const searchParams = useSearchParams()
  const roomId = params.roomId as string
  const roomName = searchParams.get("name") || `Room ${roomId}`
  const isHost = searchParams.get("host") === "true"

  const [isVRMode, setIsVRMode] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isVideoOn, setIsVideoOn] = useState(true)
  const [isScreenSharing, setIsScreenSharing] = useState(false)
  const [showWhiteboard, setShowWhiteboard] = useState(false)
  const [participants, setParticipants] = useState<Participant[]>([
    {
      id: "user-1",
      name: "You",
      isHost: isHost,
      isMuted: false,
      isVideoOn: true,
      avatar: {
        position: [0, 0, 0],
        rotation: [0, 0, 0],
      },
    },
    {
      id: "user-2",
      name: "Alice Johnson",
      isHost: false,
      isMuted: false,
      isVideoOn: true,
      avatar: {
        position: [2, 0, -1],
        rotation: [0, -0.5, 0],
      },
    },
    {
      id: "user-3",
      name: "Bob Smith",
      isHost: false,
      isMuted: true,
      isVideoOn: false,
      avatar: {
        position: [-2, 0, -1],
        rotation: [0, 0.5, 0],
      },
    },
  ])

  const vrRef = useRef<any>(null)

  useEffect(() => {
    // Initialize WebRTC and Socket.io connections here
    console.log(`Joining room: ${roomId}`)

    // Cleanup on unmount
    return () => {
      console.log(`Leaving room: ${roomId}`)
    }
  }, [roomId])

  const toggleVRMode = async () => {
    if (!isVRMode) {
      try {
        if (vrRef.current) {
          await vrRef.current.enterVR()
          setIsVRMode(true)
        }
      } catch (error) {
        console.error("Failed to enter VR mode:", error)
        alert("VR mode not supported or no VR device detected")
      }
    } else {
      if (vrRef.current) {
        await vrRef.current.exitVR()
        setIsVRMode(false)
      }
    }
  }

  const toggleMute = () => {
    setIsMuted(!isMuted)
    // TODO: Implement actual audio muting
  }

  const toggleVideo = () => {
    setIsVideoOn(!isVideoOn)
    // TODO: Implement actual video toggle
  }

  const toggleScreenShare = () => {
    setIsScreenSharing(!isScreenSharing)
    // TODO: Implement screen sharing
  }

  const leaveRoom = () => {
    window.location.href = "/classroom"
  }

  return (
    <div className="h-screen bg-black relative overflow-hidden">
      {/* VR Classroom Scene */}
      <div className="absolute inset-0">
        <VRClassroom
          ref={vrRef}
          participants={participants}
          isVRMode={isVRMode}
          showWhiteboard={showWhiteboard}
          roomId={roomId}
        />
      </div>

      {/* UI Overlay */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top Bar */}
        <div className="absolute top-4 left-4 right-4 flex items-center justify-between pointer-events-auto">
          <div className="flex items-center gap-4">
            <Card className="bg-black/80 backdrop-blur-sm border-gray-700">
              <CardContent className="p-3">
                <div className="flex items-center gap-3">
                  <Users className="h-5 w-5 text-white" />
                  <div>
                    <h2 className="text-white font-semibold">{roomName}</h2>
                    <p className="text-gray-300 text-sm">Room: {roomId}</p>
                  </div>
                  {isVRMode && <Badge variant="secondary">VR Mode</Badge>}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setShowWhiteboard(!showWhiteboard)}>
              Whiteboard
            </Button>
            <Button variant="outline" size="sm" onClick={leaveRoom}>
              <ExitIcon className="h-4 w-4 mr-2" />
              Leave
            </Button>
          </div>
        </div>

        {/* Bottom Controls */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 pointer-events-auto">
          <Card className="bg-black/80 backdrop-blur-sm border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <Button
                  variant={isMuted ? "destructive" : "outline"}
                  size="sm"
                  onClick={toggleMute}
                  className="text-white border-gray-600"
                >
                  {isMuted ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </Button>

                <Button
                  variant={!isVideoOn ? "destructive" : "outline"}
                  size="sm"
                  onClick={toggleVideo}
                  className="text-white border-gray-600"
                >
                  {isVideoOn ? <Video className="h-4 w-4" /> : <VideoOff className="h-4 w-4" />}
                </Button>

                <Button
                  variant={isScreenSharing ? "default" : "outline"}
                  size="sm"
                  onClick={toggleScreenShare}
                  className="text-white border-gray-600"
                >
                  <Share className="h-4 w-4" />
                </Button>

                <div className="w-px h-6 bg-gray-600" />

                <Button
                  variant={isVRMode ? "default" : "outline"}
                  size="sm"
                  onClick={toggleVRMode}
                  className="text-white border-gray-600"
                >
                  {isVRMode ? <Monitor className="h-4 w-4" /> : <Headphones className="h-4 w-4" />}
                  {isVRMode ? "Exit VR" : "Enter VR"}
                </Button>

                <Button variant="outline" size="sm" className="text-white border-gray-600 bg-transparent">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Participants Panel */}
        <div className="absolute top-20 right-4 pointer-events-auto">
          <ParticipantsList participants={participants} />
        </div>

        {/* Virtual Whiteboard */}
        {showWhiteboard && (
          <div className="absolute top-20 left-4 pointer-events-auto">
            <VirtualWhiteboard onClose={() => setShowWhiteboard(false)} />
          </div>
        )}
      </div>
    </div>
  )
}
