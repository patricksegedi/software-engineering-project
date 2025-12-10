import { useEffect, useState } from "react"
import "./ZoneManagement.css"
import { getZonesApi, createZoneApi, deleteZoneApi } from "../../api/zones"

export default function ZoneManagement() {
  const [zones, setZones] = useState([])
  const [newZoneName, setNewZoneName] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadZones() {
      try {
        const data = await getZonesApi()
        setZones(data)
      } catch (err) {
        console.error(err)
        alert("서버에서 존 목록을 불러오지 못했습니다.")
      } finally {
        setLoading(false)
      }
    }
    loadZones()
  }, [])

  const handleAddZone = async (e) => {
    e.preventDefault()
    const trimmed = newZoneName.trim()
    if (!trimmed) return

    try {
      const created = await createZoneApi({ name: trimmed })
      setZones((prev) => [...prev, created])
      setNewZoneName("")
    } catch (err) {
      console.error(err)
      alert("존을 생성하는 중 오류가 발생했습니다.")
    }
  }

  const handleDeleteZone = async (id) => {
    if (!window.confirm("이 존을 삭제하시겠습니까? 관련 디바이스도 함께 삭제됩니다.")) return
    try {
      await deleteZoneApi(id)
      setZones((prev) => prev.filter((z) => z.id !== id))
    } catch (err) {
      console.error(err)
      alert("존을 삭제하는 중 오류가 발생했습니다.")
    }
  }

  return (
    <div className="zones-container">
      <header className="zones-header">
        <h1 className="zones-title">Zone management</h1>
        <p className="zones-subtitle">
          집 안의 공간들을 존으로 정의하고, 디바이스를 연결할 수 있습니다.
        </p>
      </header>

      <section className="zones-section">
        <h2 className="zones-section-title">Add new zone</h2>

        <form className="zones-form" onSubmit={handleAddZone}>
          <input
            className="zones-input"
            type="text"
            placeholder="e.g. Living room, Kitchen"
            value={newZoneName}
            onChange={(e) => setNewZoneName(e.target.value)}
          />
          <button className="zones-add-btn" type="submit">
            Add zone
          </button>
        </form>
      </section>

      <section className="zones-section">
        <h2 className="zones-section-title">Existing zones</h2>

        {loading ? (
          <p className="zones-empty">Loading zones...</p>
        ) : (
          <div className="zones-list">
            {zones.map((zone) => (
              <div key={zone.id} className="zone-item">
                <div className="zone-main">
                  <div className="zone-badge">
                    {zone.display_name || zone.name}
                  </div>
                  <span className="zone-name">
                    Internal name: <strong>{zone.name}</strong>
                  </span>
                </div>
                <button
                  className="zone-remove-btn"
                  type="button"
                  onClick={() => handleDeleteZone(zone.id)}
                >
                  Remove
                </button>
              </div>
            ))}

            {zones.length === 0 && !loading && (
              <p className="zones-empty">No zones defined yet.</p>
            )}
          </div>
        )}
      </section>
    </div>
  )
}
