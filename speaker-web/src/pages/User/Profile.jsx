// src/pages/User/Profile.jsx
import { useState, useRef } from "react"
import { useAuth } from "../../AuthContext"
import "./Profile.css"

const VOICES = ["Luna", "Mira", "Oscar"]

const TRAINING_SENTENCES = [
  "Hi, this is my personal smart speaker.",
  "Turn on the living room lights, please.",
  "Good night, lock the main door.",
]

const demoUser = {
  email: "user@example.com",
  role: "User",
  familyRole: "Father",
}

export default function Profile() {
  const { user } = useAuth()

  // Assistant voice
  const [selectedVoice, setSelectedVoice] = useState("Luna")

  // Voice training
  const [isRecording, setIsRecording] = useState(false)
  const [trainingStatus, setTrainingStatus] = useState("Not started")

  // ✅ MediaRecorder용 ref들
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  const uploadRecording = async (blob) => {
    try {
      if (!user?.id) {
        alert("로그인이 필요합니다.")
        return
      }

      const fd = new FormData()
      fd.append("file", blob, "voice.webm") // webm으로 보냄

      const res = await fetch(
        `http://127.0.0.1:8000/users/${user.id}/voice-profile`,
        {
          method: "POST",
          body: fd,
        }
      )

      if (!res.ok) {
        const txt = await res.text()
        throw new Error(txt)
      }

      setTrainingStatus("Completed")
      alert("녹음한 음성이 DB에 저장되었습니다.")
    } catch (err) {
      console.error(err)
      setTrainingStatus("Error")
      alert("업로드 중 오류가 발생했습니다.")
    }
  }

  const startOrStopTraining = async () => {
    // 이미 녹음 중이면 → stop + 업로드
    if (isRecording) {
      const mr = mediaRecorderRef.current
      if (mr && mr.state !== "inactive") {
        mr.stop()
      }
      setIsRecording(false)
      setTrainingStatus("Uploading…")
      return
    }

    // 녹음 시작
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mr = new MediaRecorder(stream)

      chunksRef.current = []

      mr.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mr.onstop = async () => {
        // stream 정리
        stream.getTracks().forEach((t) => t.stop())

        // 모든 chunk 합쳐서 Blob 생성
        const blob = new Blob(chunksRef.current, { type: "audio/webm" })

        // 디버깅: 실제 길이 확인하고 싶으면 브라우저에서 재생해볼 수도 있음
        // const url = URL.createObjectURL(blob)
        // const audio = new Audio(url)
        // audio.play()

        await uploadRecording(blob)
      }

      mr.start() // 사용자가 Stop 누를 때까지 계속 녹음
      mediaRecorderRef.current = mr

      setIsRecording(true)
      setTrainingStatus("Recording…")
    } catch (err) {
      console.error(err)
      alert("마이크에 접근할 수 없습니다. 브라우저 권한을 확인해주세요.")
    }
  }

  return (
    <div className="profile-container">
      <h1 className="profile-title">My profile</h1>
      <p className="profile-subtitle">
        Manage your account, family role and voice preferences.
      </p>

      <div className="profile-grid">
        {/* Account card */}
        <section className="profile-card">
          <h2 className="profile-card-title">Account</h2>
          <p className="profile-field">
            <span> Email </span>
            <strong>{demoUser.email}</strong>
          </p>
          <p className="profile-field">
            <span> Role </span>
            <strong>{demoUser.role}</strong>
          </p>
          <p className="profile-field">
            <span> Family role </span>
            <strong>{demoUser.familyRole}</strong>
          </p>
          <p className="profile-hint">
            (In a real system, this would come from your account settings.)
          </p>
        </section>

        {/* Assistant voice card */}
        <section className="profile-card">
          <h2 className="profile-card-title">Assistant voice</h2>
          <p className="profile-text">
            Choose how your smart speaker sounds. This is your personal voice
            profile.
          </p>

          <div className="voice-select-row">
            {VOICES.map((voice) => (
              <button
                key={voice}
                type="button"
                className={`voice-pill ${
                  selectedVoice === voice ? "voice-pill-selected" : ""
                }`}
                onClick={() => setSelectedVoice(voice)}
              >
                {voice}
              </button>
            ))}
          </div>

          <p className="selected-voice-text">
            Current voice: <strong>{selectedVoice}</strong>
          </p>

          <button
            type="button"
            className="primary-btn"
            onClick={() => alert("Demo only – no backend connected")}
          >
            Save changes
          </button>
        </section>
      </div>

      {/* Voice training section */}
      <section className="profile-section">
        <h2>Train your voice</h2>
        <p>
          Teach the speaker how you sound. This will record a short sample of
          your voice and save it to the smart speaker.
        </p>

        <p>
          Training status: <strong>{trainingStatus}</strong>
        </p>

        <button
          type="button"
          className="primary-btn"
          onClick={startOrStopTraining}
        >
          {isRecording ? "Stop & upload" : "Start training"}
        </button>

        <p style={{ fontSize: 12, marginTop: 8, color: "#666" }}>
          {isRecording
            ? "지금 말하세요... 다시 버튼을 누르면 녹음이 종료되고 업로드됩니다."
            : "버튼을 누른 뒤 평소처럼 3–5초 정도 자연스럽게 말해 주세요."}
        </p>
      </section>
    </div>
  )
}
