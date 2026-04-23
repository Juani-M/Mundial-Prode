import { useEffect, useState } from 'react'
import './App.css'

function Navbar({ activeTab, setActiveTab }) {
  return (
    <nav style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '2rem' }}>
      <button 
        onClick={() => setActiveTab('fixture')}
        style={{ 
          fontWeight: activeTab === 'fixture' ? 'bold' : 'normal',
          background: activeTab === 'fixture' ? '#e3f2fd' : '#f8f9fa',
          border: '1px solid #dee2e6',
          padding: '0.5rem 1.5rem',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Fixture
      </button>
      <button 
        onClick={() => setActiveTab('ranking')}
        style={{ 
          fontWeight: activeTab === 'ranking' ? 'bold' : 'normal',
          background: activeTab === 'ranking' ? '#e3f2fd' : '#f8f9fa',
          border: '1px solid #dee2e6',
          padding: '0.5rem 1.5rem',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Ranking
      </button>
    </nav>
  )
}

function Fixture() {
  const [matches, setMatches] = useState([])
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedPhase, setSelectedPhase] = useState('Grupos')

  const phases = ['Grupos', '16avos', 'Octavos', 'Cuartos', 'Semifinal', 'Final']
  const expectedMatches = {
    '16avos': 16,
    'Octavos': 8,
    'Cuartos': 4,
    'Semifinal': 2,
    'Final': 1
  }

  useEffect(() => {
    // Simulamos el usuario 1 logueado
    const userId = 1;
    
    Promise.all([
      fetch('http://127.0.0.1:8000/api/v1/matches/').then(res => res.json()),
      fetch(`http://127.0.0.1:8000/api/v1/predictions/user/${userId}`).then(res => res.json())
    ])
      .then(([matchesData, predictionsData]) => {
        setMatches(matchesData)
        setPredictions(Array.isArray(predictionsData) ? predictionsData : [])
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  if (loading) return <p style={{textAlign: 'center'}}>Cargando fixture...</p>

  // Filtrar partidos por la fase seleccionada
  let filteredMatches = matches.filter(m => m.phase === selectedPhase)
  
  // Rellenar con placeholders si es fase eliminatoria y faltan partidos
  if (expectedMatches[selectedPhase]) {
    const definedCount = filteredMatches.length;
    const required = expectedMatches[selectedPhase];
    if (definedCount < required) {
      const placeholders = Array.from({ length: required - definedCount }).map((_, i) => ({
        id: `placeholder-${selectedPhase}-${i}`,
        team_home: 'Por definir',
        team_away: 'Por definir',
        phase: selectedPhase,
        status: 'pending',
        isPlaceholder: true
      }))
      filteredMatches = [...filteredMatches, ...placeholders]
    }
  }

  return (
    <div>
      <h2 style={{ color: '#34495e', borderBottom: '2px solid #eee', paddingBottom: '0.5rem' }}>Fixture de Partidos</h2>
      
      {/* Selector de Fases */}
      <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.5rem', marginTop: '1rem' }}>
        {phases.map(phase => (
          <button
            key={phase}
            onClick={() => setSelectedPhase(phase)}
            style={{
              padding: '0.4rem 1rem',
              borderRadius: '20px',
              border: '1px solid #0ea5e9',
              background: selectedPhase === phase ? '#0ea5e9' : 'transparent',
              color: selectedPhase === phase ? '#fff' : '#0ea5e9',
              fontWeight: 'bold',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s'
            }}
          >
            {phase}
          </button>
        ))}
      </div>

      <ul style={{ listStyle: 'none', padding: 0, display: 'grid', gap: '1rem', marginTop: '1.5rem' }}>
        {filteredMatches.map(match => {
          const userPrediction = !match.isPlaceholder ? predictions.find(p => p.match_id === match.id) : null
          
          let cardBg = '#ffffff'; // Pendiente (Blanco)
          let textColor = '#334155'; // Texto oscuro
          let scoreColor = '#334155';
          let vsColor = '#64748b'; // VS gris oscuro
          let predBoxBg = 'rgba(0,0,0,0.03)';
          let cardBorder = '2px solid #000000'; // Borde negro
          
          if (match.status === 'finished') {
            cardBg = '#0F172A'; // Terminado (Negro suave)
            textColor = '#f8fafc'; // Texto claro
            scoreColor = '#f8fafc';
            vsColor = '#94a3b8'; // VS gris claro
            predBoxBg = 'rgba(255,255,255,0.05)';
            cardBorder = '2px solid #000000'; 
          } else if (match.status === 'in_progress' || match.status === 'en_curso') {
            cardBg = '#2563eb'; // En curso (Azul)
            textColor = '#f8fafc'; // Texto claro
            scoreColor = '#34D399'; // Verde fluorescente para el resultado
            vsColor = '#93c5fd'; // VS celeste
            predBoxBg = 'rgba(255,255,255,0.1)';
            cardBorder = '2px solid #000000'; 
          }

          const isPlaceholder = match.isPlaceholder;

          let predBoxShadow = 'none';
          let predBorderColor = match.status === 'pending' || !match.status ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.2)';
          if (userPrediction && userPrediction.points_earned !== null) {
            if (userPrediction.points_earned === 2) {
              predBoxShadow = 'inset 0 0 30px rgba(234, 179, 8, 0.4)'; // Dorado suave
              predBorderColor = 'rgba(234, 179, 8, 0.8)';
            } else if (userPrediction.points_earned === 1) {
              predBoxShadow = 'inset 0 0 30px rgba(255, 255, 255, 0.3)'; // Blanco suave
              predBorderColor = 'rgba(255, 255, 255, 0.8)';
            } else if (userPrediction.points_earned === 0) {
              predBoxShadow = 'inset 0 0 30px rgba(239, 68, 68, 0.4)'; // Rojo suave
              predBorderColor = 'rgba(239, 68, 68, 0.8)';
            }
          }

          return (
            <li key={match.id} style={{ background: cardBg, color: textColor, border: cardBorder, borderRadius: '8px', padding: '1.5rem', opacity: isPlaceholder ? 0.6 : 1, boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', gap: '1rem' }}>
                <span style={{ flex: 1, fontSize: 'clamp(1rem, 2.5vw, 1.25rem)', fontWeight: 'bold', wordBreak: 'break-word', textAlign: 'center', color: isPlaceholder ? '#94a3b8' : textColor }}>{match.team_home}</span>
                <span style={{ color: vsColor, fontWeight: 'bold', flexShrink: 0 }}>VS</span>
                <span style={{ flex: 1, fontSize: 'clamp(1rem, 2.5vw, 1.25rem)', fontWeight: 'bold', wordBreak: 'break-word', textAlign: 'center', color: isPlaceholder ? '#94a3b8' : textColor }}>{match.team_away}</span>
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem', color: textColor, alignItems: 'center' }}>
                {(match.status === 'finished' || match.status === 'in_progress' || match.status === 'en_curso') && !isPlaceholder && (
                    <span style={{ color: scoreColor, fontWeight: 'bold', fontSize: '1.5rem', margin: '0.5rem 0' }}>
                      {match.score_home_actual} - {match.score_away_actual}
                    </span>
                )}

                {/* Predicción destacada (no se muestra si es placeholder) */}
                {!isPlaceholder && (
                  <div style={{ background: predBoxBg, border: `1px solid ${predBorderColor}`, boxShadow: predBoxShadow, padding: '0.75rem', borderRadius: '6px', marginTop: '0.5rem', width: '100%', textAlign: 'center', transition: 'all 0.3s' }}>
                    <strong>Tu Predicción:</strong>{' '}
                    {userPrediction ? (
                      <span>
                        <span style={{fontSize: '1.1rem'}}>{userPrediction.score_home_predicted} - {userPrediction.score_away_predicted}</span>
                        {userPrediction.points_earned !== null && (
                          <span style={{ marginLeft: '0.5rem', color: userPrediction.points_earned === 2 ? '#facc15' : userPrediction.points_earned === 1 ? '#e2e8f0' : '#f87171', fontWeight: 'bold' }}>
                            (Puntos ganados: {userPrediction.points_earned})
                          </span>
                        )}
                      </span>
                    ) : (
                      <span style={{ color: '#94a3b8', fontStyle: 'italic' }}>No realizaste predicción</span>
                    )}
                  </div>
                )}
              </div>
            </li>
          )
        })}
        {filteredMatches.length === 0 && <p style={{ textAlign: 'center' }}>No hay partidos cargados para esta fase.</p>}
      </ul>
    </div>
  )
}

function Ranking() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/v1/users/ranking')
      .then(res => res.json())
      .then(data => {
        setUsers(data)
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  if (loading) return <p style={{textAlign: 'center'}}>Cargando ranking...</p>

  return (
    <div>
      <h2 style={{ color: '#34495e', borderBottom: '2px solid #eee', paddingBottom: '0.5rem' }}>Ranking Global</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem', background: 'white' }}>
        <thead>
          <tr style={{ background: '#f1f3f5', textAlign: 'left' }}>
            <th style={{ padding: '0.75rem', borderBottom: '2px solid #dee2e6' }}>Pos.</th>
            <th style={{ padding: '0.75rem', borderBottom: '2px solid #dee2e6' }}>Usuario</th>
            <th style={{ padding: '0.75rem', borderBottom: '2px solid #dee2e6', textAlign: 'center' }}>Puntos</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user, index) => (
            <tr key={user.id} style={{ borderBottom: '1px solid #e9ecef' }}>
              <td style={{ padding: '0.75rem', fontWeight: 'bold', color: '#495057', width: '15%' }}>#{index + 1}</td>
              <td style={{ padding: '0.75rem', wordBreak: 'break-word', maxWidth: '200px' }}>{user.username}</td>
              <td style={{ padding: '0.75rem', fontWeight: 'bold', color: '#1565c0', textAlign: 'center', width: '20%' }}>{user.total_points}</td>
            </tr>
          ))}
          {users.length === 0 && (
            <tr>
              <td colSpan="3" style={{ padding: '1rem', textAlign: 'center', color: '#868e96' }}>No hay usuarios registrados.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

function App() {
  const [activeTab, setActiveTab] = useState('fixture')

  return (
    <main style={{ 
      background: 'rgba(255, 255, 255, 0.95)', 
      padding: '2rem', 
      fontFamily: 'system-ui, sans-serif', 
      maxWidth: '800px', 
      margin: '2rem auto',
      borderRadius: '16px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.2)' 
    }}>
      <h1 style={{ textAlign: 'center', color: '#2c3e50', marginBottom: '2rem' }}>🏆 Prode Mundial</h1>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      {activeTab === 'fixture' && <Fixture />}
      {activeTab === 'ranking' && <Ranking />}
    </main>
  )
}

export default App
