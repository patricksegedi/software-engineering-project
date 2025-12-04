import { useState } from "react"
import { useAuth } from "../../AuthContext"

export default function VoiceEnroll() {
  const { user } = useAuth()
  const [recorder, setRecorder] = useState(null)
  const [chunks, setChunks] = useState([])

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mr = new MediaRecorder(stream)

    setChunks([])
    mr.ondataavailable = (e) => setChunks((prev) => [...prev, e.data])
    mr.onstop = () => {
      const blob = new Blob(chunks, { type: "audio/webm" })
      upload(blob)
    }
    mr.start()
    setRecorder(mr)
  }

  const stop = () => {
    recorder?.stop()
  }

  const upload = async (blob) => {
    const fd = new FormData()
    // 스피커 쪽 name은 회원가입 때 보낸 name과 맞춰야 함
    const speakerName = user.email.split("@")[0]

    fd.append("file", blob, "voice.webm")

    await fetch(`http://127.0.0.1:8000/users/${speakerName}/voice`, {
      method: "POST",
      body: fd,
    })
    alert("음성 등록 완료!")
  }

  return (
    <div>
      <h2>Voice enrollment</h2>
      <button onClick={start}>녹음 시작</button>
      <button onClick={stop}>녹음 종료</button>
    </div>
  )
}
