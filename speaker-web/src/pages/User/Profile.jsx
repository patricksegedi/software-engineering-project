// src/pages/User/Profile.jsx
import { useState } from "react"
import { useAuth } from "../../AuthContext"
import "./Profile.css"

const VOICES = ["Luna", "Mira", "Oscar"]

const TRAINING_SENTENCES = [
  "Hi, this is my personal smart speaker.",
  "Turn on the living room lights, please.",
  "Good night, lock the main door.",
]

// 데모용 유저 정보 (Auth 연동 전)
const demoUser = {
  email: "user@example.com",
  role: "User",
  familyRole: "Father",
}

// ===== WAV 인코딩용 헬퍼 함수 & 전역 변수들 =====

// 녹음 버퍼들을 하나로 합치기
function mergeBuffers(channelBuffer, recordingLength) {
  const result = new Float32Array(recordingLength)
  let offset = 0
  for (let i = 0; i < channelBuffer.length; i++) {
    result.set(channelBuffer[i], offset)
    offset += channelBuffer[i].length
  }
  return result
}

// Float32Array PCM 데이터를 WAV 포맷 Blob으로 변환
function encodeWAV(samples, sampleRate) {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)

  function writeString(offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i))
    }
  }

  // RIFF 헤더
  writeString(0, "RIFF")
  view.setUint32(4, 36 + samples.length * 2, true)
  writeString(8, "WAVE")
  writeString(12, "fmt ")
  view.setUint32(16, 16, true) // fmt chunk size
  view.setUint16(20, 1, true) // audio format (1 = PCM)
  view.setUint16(22, 1, true) // num channels
  view.setUint32(24, sampleRate, true) // sample rate
  view.setUint32(28, sampleRate * 2, true) // byte rate
  view.setUint16(32, 2, true) // block align
  view.setUint16(34, 16, true) // bits per sample
  writeString(36, "data")
  view.setUint32(40, samples.length * 2, true)

  // 실제 PCM 데이터(16bit LE)
  let offset = 44
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }

  return new Blob([view], { type: "audio/wav" })
}

// 오디오 녹음을 위한 전역 변수들 (컴포넌트 밖에 둬서 렌더 사이에서도 유지)
let audioContext = null
let processor = null
let inputNode = null
let stream = null
let leftChannel = []
let recordingLength = 0
let sampleRate = 44100
// ===============================================

export default function Profile() {
  const { user } = useAuth()

  // Assistant voice 선택용 state
  const [selectedVoice, setSelectedVoice] = useState("Luna")

  // 🔉 음성 학습용 state
  const [isRecording, setIsRecording] = useState(false)
  const [trainingStatus, setTrainingStatus] = useState("Not started")

  // 1) 서버로 WAV 파일 업로드
  const uploadRecording = async (blob) => {
    try {
      // 스피커 쪽 username = 이메일 앞부분 (회원가입 때 보낸 것과 동일)
      const email = user?.email || demoUser.email
      const username = email.split("@")[0]

      const fd = new FormData()
      fd.append("file", blob, "voice.wav") // 🔥 여기서 확장자를 wav로 사용

      const res = await fetch(`http://127.0.0.1:8000/users/${username}/voice`, {
        method: "POST",
        body: fd,
      })

      if (!res.ok) {
        const txt = await res.text()
        throw new Error(txt)
      }

      setTrainingStatus("Completed")
      alert("녹음한 WAV 음성이 스피커에 저장되었습니다.")
    } catch (err) {
      console.error(err)
      setTrainingStatus("Failed")
      alert("업로드에 실패했습니다: " + err.message)
    } finally {
      setIsRecording(false)
    }
  }

  // 2) 녹음 시작/종료 토글 (AudioContext 사용, WAV로 변환)
  const startOrStopTraining = async () => {
    // 이미 녹음 중이면 → 종료 + WAV 생성 + 업로드
    if (isRecording) {
      if (processor) processor.disconnect()
      if (inputNode) inputNode.disconnect()
      if (audioContext) await audioContext.close()
      if (stream) stream.getTracks().forEach((t) => t.stop())

      // 버퍼 합치고 WAV로 인코딩
      const samples = mergeBuffers(leftChannel, recordingLength)
      const wavBlob = encodeWAV(samples, sampleRate)

      // 다음 녹음을 위해 초기화
      leftChannel = []
      recordingLength = 0

      // 서버로 업로드
      await uploadRecording(wavBlob)
      return
    }

    // 녹음 시작
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioContext = new (window.AudioContext || window.webkitAudioContext)()
      sampleRate = audioContext.sampleRate

      inputNode = audioContext.createMediaStreamSource(stream)
      processor = audioContext.createScriptProcessor(4096, 1, 1)

      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0)
        leftChannel.push(new Float32Array(inputData))
        recordingLength += inputData.length
      }

      inputNode.connect(processor)
      processor.connect(audioContext.destination)

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
        {/* User info card */}
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

        {/* Voice profile card */}
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
            : "버튼을 누른 뒤 2–3초 정도 평소처럼 말해 주세요."}
        </p>
      </section>
    </div>
  )
}
