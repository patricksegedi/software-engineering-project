// src/pages/User/Profile.jsx
import { useState } from "react"
import "./Profile.css"

const VOICES = ["Luna", "Mira", "Oscar"]

const TRAINING_SENTENCES = [
  "Hi, this is my personal smart speaker.",
  "Turn on the living room lights, please.",
  "Good night, lock the main door.",
]

export default function Profile() {
  // demo: normally these would come from backend / auth
  const demoUser = {
    email: "user@example.com",
    role: "User",
    familyRole: "Father",
  }

  const [selectedVoice, setSelectedVoice] = useState("Luna")
  // 0 = idle, 1~3 = steps, 4 = done
  const [trainingStep, setTrainingStep] = useState(0)

  const startTraining = () => {
    setTrainingStep(1)
  }

  const cancelTraining = () => {
    setTrainingStep(0)
  }

  const nextSentence = () => {
    if (trainingStep >= 1 && trainingStep < 3) {
      setTrainingStep(trainingStep + 1)
    } else if (trainingStep === 3) {
      setTrainingStep(4) // completed
    }
  }

  const restartTraining = () => {
    setTrainingStep(1)
  }

  const currentSentence =
    trainingStep >= 1 && trainingStep <= 3
      ? TRAINING_SENTENCES[trainingStep - 1]
      : null

  const stepLabel =
    trainingStep >= 1 && trainingStep <= 3
      ? `Step ${trainingStep} of 3`
      : trainingStep === 4
      ? "Completed"
      : "Not started"

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
      <section className="profile-card training-card">
        <h2 className="profile-card-title">Train your voice</h2>
        <p className="profile-text">
          Teach the speaker how you sound. This is a demo of voice training,
          similar to the first setup in Bixby. No real audio is recorded.
        </p>

        <p className="training-status">
          Training status: <strong>{stepLabel}</strong>
        </p>

        {trainingStep === 0 && (
          <div className="training-idle">
            <p className="profile-text">
              We will ask you to read 3 short sentences. This helps us
              personalize your experience.
            </p>
            <button
              type="button"
              className="primary-btn"
              onClick={startTraining}
            >
              Start training
            </button>
          </div>
        )}

        {trainingStep >= 1 && trainingStep <= 3 && (
          <div className="training-active">
            <p className="training-step-label">Step {trainingStep} of 3</p>
            <div className="training-sentence-box">
              <p className="training-sentence">“{currentSentence}”</p>
            </div>

            <div className="training-mic-box">
              <div className="training-mic-icon">🎙</div>
              <p className="training-mic-text">
                Imagine the system is listening to your voice.
              </p>
            </div>

            <div className="training-actions">
              <button
                type="button"
                className="primary-btn"
                onClick={nextSentence}
              >
                Next sentence
              </button>
              <button
                type="button"
                className="secondary-btn"
                onClick={cancelTraining}
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {trainingStep === 4 && (
          <div className="training-complete">
            <div className="training-complete-icon">✅</div>
            <p className="training-complete-text">
              Voice training completed. Your speaker is now better tuned to your
              voice. (Demo only)
            </p>
            <button
              type="button"
              className="primary-btn"
              onClick={restartTraining}
            >
              Train again
            </button>
          </div>
        )}
      </section>
    </div>
  )
}
