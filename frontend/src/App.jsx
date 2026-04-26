import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Calendar, PenLine, Trophy, Sun, Moon } from 'lucide-react'
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const BANDERAS = {
  "Argentina": "ar", "Brasil": "br", "Alemania": "de", "Polonia": "pl",
  "Francia": "fr", "Inglaterra": "gb-eng", "España": "es", "Portugal": "pt",
  "Países Bajos": "nl", "Croacia": "hr", "Marruecos": "ma", "Estados Unidos": "us",
  "Uruguay": "uy", "México": "mx", "Japón": "jp", "Corea del Sur": "kr",
  "Senegal": "sn", "Gales": "gb-wls", "Australia": "au", "Ecuador": "ec",
  "Arabia Saudita": "sa", "Canadá": "ca", "Camerún": "cm", "Suiza": "ch",
  "Bélgica": "be", "Dinamarca": "dk", "Túnez": "tn", "Irán": "ir",
  "Costa Rica": "cr", "Serbia": "rs", "Ghana": "gh",
  "Algeria": "dz", "Austria": "at", "Bosnia-Herzegovina": "ba", 
  "Cape Verde Islands": "cv", "Colombia": "co", "Congo DR": "cd", 
  "Curaçao": "cw", "Czechia": "cz", "Egypt": "eg", "Haiti": "ht", 
  "Iraq": "iq", "Ivory Coast": "ci", "Jordan": "jo", "New Zealand": "nz", 
  "Norway": "no", "Panama": "pa", "Paraguay": "py", "Qatar": "qa", 
  "Scotland": "gb-sct", "South Africa": "za", "Sweden": "se", 
  "Turkey": "tr", "Uzbekistan": "uz"
};

function TeamConBandera({ team, isPlaceholder, isAway }) {
  if (isPlaceholder) return <span className="team-name" style={{ color: '#94a3b8' }}>{team}</span>;
  const isoCode = BANDERAS[team];
  return (
    <span className="team-name" style={{ flexDirection: isAway ? 'row-reverse' : 'row' }}>
      {isoCode ? (
        <img 
          src={`https://flagcdn.com/w40/${isoCode}.png`} 
          width="24" 
          alt={`Bandera de ${team}`} 
          className="flag-icon-img"
          style={{ borderRadius: '2px', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }}
        />
      ) : (
        <span className="flag-icon" style={{ fontSize: '1.1rem' }}>🏳️</span>
      )}
      <span className="team-text">{team}</span>
    </span>
  );
}

function BottomNav({ activeTab, setActiveTab }) {
  return (
    <nav className="bottom-nav">
      <button className={`nav-item ${activeTab === 'fixture' ? 'active' : ''}`} onClick={() => setActiveTab('fixture')}>
        <Calendar size={24} />
        <span>Fixture</span>
      </button>
      <button className={`nav-item ${activeTab === 'predicciones' ? 'active' : ''}`} onClick={() => setActiveTab('predicciones')}>
        <PenLine size={24} />
        <span>Predicciones</span>
      </button>
      <button className={`nav-item ${activeTab === 'ranking' ? 'active' : ''}`} onClick={() => setActiveTab('ranking')}>
        <Trophy size={24} />
        <span>Ranking</span>
      </button>
    </nav>
  )
}

function Fixture({ userId }) {
  const [matches, setMatches] = useState([])
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedPhase, setSelectedPhase] = useState('Fase de Grupos')
  const [expandedGroups, setExpandedGroups] = useState({}) 

  const phases = ['Fase de Grupos', '16avos', 'Octavos', 'Cuartos', 'Semifinal', 'Final']

  useEffect(() => {
    // const userId = 1; // Passed via props
    Promise.all([
      fetch(`${API_BASE}/api/v1/matches/`).then(res => res.json()),
      fetch(`${API_BASE}/api/v1/predictions/user/${userId}`).then(res => res.json())
    ]).then(([matchesData, predictionsData]) => {
        setMatches(matchesData)
        setPredictions(Array.isArray(predictionsData) ? predictionsData : [])
        setLoading(false)
    }).catch(err => { console.error(err); setLoading(false) })
  }, [])

  const toggleGroup = (groupName) => {
    setExpandedGroups(prev => ({ ...prev, [groupName]: !prev[groupName] }))
  }

  if (loading) return <p style={{textAlign: 'center'}}>Cargando fixture...</p>

  let filteredMatches = matches.filter(m => 
    selectedPhase === 'Fase de Grupos' ? m.phase.startsWith('Grupo') : m.phase === selectedPhase
  )
  
  const groupedMatches = filteredMatches.reduce((acc, match) => {
    if (!acc[match.phase]) acc[match.phase] = [];
    acc[match.phase].push(match);
    return acc;
  }, {});

  const sortedGroups = Object.keys(groupedMatches).sort();

  return (
    <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
      <h2 className="section-title">Resultados y Fixture</h2>
      <div className="phase-selector">
        {phases.map(phase => (
          <button key={phase} onClick={() => setSelectedPhase(phase)} className={selectedPhase === phase ? 'active' : ''}>
            {phase}
          </button>
        ))}
      </div>

      {sortedGroups.length === 0 ? (
         <p style={{ textAlign: 'center', marginTop: '2rem' }}>No hay partidos cargados.</p>
      ) : (
        sortedGroups.map(groupName => {
          const isExpanded = expandedGroups[groupName] || false;
          return (
            <div key={groupName} className="group-header-card" style={{ marginBottom: '1rem', background: '#f8fafc', borderRadius: '8px', padding: '0 1rem', border: '1px solid #e2e8f0' }}>
              <h3 onClick={() => toggleGroup(groupName)}
                style={{ color: '#1e293b', fontSize: '1.25rem', padding: '1rem 0', margin: '0', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', userSelect: 'none' }}>
                <span>{groupName}</span>
                <motion.span animate={{ rotate: isExpanded ? 180 : 0 }} style={{ fontSize: '0.9rem', color: '#64748b' }}>▼</motion.span>
              </h3>
              
              <AnimatePresence>
              {isExpanded && (
                <motion.ul 
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  style={{ overflow: 'hidden', margin: 0, padding: 0 }}
                  className="match-list"
                >
                  <div style={{ paddingBottom: '1rem', marginTop: '1rem' }}>
                  {groupedMatches[groupName].map(match => {
                    const userPrediction = !match.isPlaceholder ? predictions.find(p => p.match_id === match.id) : null
                    let cardBg = '#ffffff'; let textColor = '#334155'; let scoreColor = '#334155'; let vsColor = '#64748b'; let predBoxBg = 'rgba(0,0,0,0.03)'; let cardBorder = '2px solid #000000';
                    
                    if (match.status === 'finished') {
                      cardBg = '#0F172A'; textColor = '#f8fafc'; scoreColor = '#f8fafc'; vsColor = '#94a3b8'; predBoxBg = 'rgba(255,255,255,0.05)'; cardBorder = '1px solid #334155';
                    } else if (match.status === 'in_progress' || match.status === 'en_curso') {
                      cardBg = '#2563eb'; textColor = '#f8fafc'; scoreColor = '#34D399'; vsColor = '#93c5fd'; predBoxBg = 'rgba(255,255,255,0.1)'; cardBorder = '1px solid #1d4ed8';
                    }

                    let predBoxShadow = 'none';
                    let predBorderColor = match.status === 'pending' || !match.status ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.2)';
                    if (userPrediction && userPrediction.points_earned !== null) {
                      if (userPrediction.points_earned === 2) { predBoxShadow = 'inset 0 0 30px rgba(234, 179, 8, 0.4)'; predBorderColor = 'rgba(234, 179, 8, 0.8)'; }
                      else if (userPrediction.points_earned === 1) { predBoxShadow = 'inset 0 0 30px rgba(255, 255, 255, 0.3)'; predBorderColor = 'rgba(255, 255, 255, 0.8)'; }
                      else if (userPrediction.points_earned === 0) { predBoxShadow = 'inset 0 0 30px rgba(239, 68, 68, 0.4)'; predBorderColor = 'rgba(239, 68, 68, 0.8)'; }
                    }

                    let dateFormatted = "Fecha no definida";
                    if (match.match_date) {
                      const utcDateStr = match.match_date.endsWith('Z') ? match.match_date : `${match.match_date}Z`;
                      dateFormatted = new Date(utcDateStr).toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires', weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
                    }

                    return (
                      <li key={match.id} className="match-card" style={match.status !== 'pending' && match.status !== undefined ? { background: cardBg, color: textColor, border: cardBorder, '--date-color': vsColor } : {}}>
                        <div className="match-date">📅 {dateFormatted}</div>
                        <div className="match-teams">
                          <TeamConBandera team={match.team_home} textColor={textColor} isAway={false} />
                          <span className="vs-text" style={{ color: vsColor }}>VS</span>
                          <TeamConBandera team={match.team_away} textColor={textColor} isAway={true} />
                        </div>
                        <div className="match-details" style={{ color: textColor }}>
                          {(match.status === 'finished' || match.status === 'in_progress' || match.status === 'en_curso') && (
                              <div className="actual-score">{match.score_home_actual} - {match.score_away_actual}</div>
                          )}
                          <div className="prediction-box" style={{ border: `1px solid ${predBorderColor}`, boxShadow: predBoxShadow }}>
                            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', opacity: 0.9, color: '#ffffff' }}>Tu Predicción</span>
                            {userPrediction ? (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginTop: '0.2rem' }}>
                                <span className="prediction-score">{userPrediction.score_home_predicted} - {userPrediction.score_away_predicted}</span>
                                {userPrediction.points_earned !== null && (
                                  <span style={{ color: userPrediction.points_earned === 2 ? '#facc15' : userPrediction.points_earned === 1 ? '#e2e8f0' : '#f87171', fontWeight: 'bold', fontSize: '1.1rem' }}>
                                    (+{userPrediction.points_earned})
                                  </span>
                                )}
                              </div>
                            ) : (<span style={{ color: 'rgba(255,255,255,0.6)', fontStyle: 'italic', marginTop: '0.4rem' }}>Ninguna</span>)}
                          </div>
                        </div>
                      </li>
                    )
                  })}
                  </div>
                </motion.ul>
              )}
              </AnimatePresence>
            </div>
          )
        })
      )}
    </motion.div>
  )
}

function Predicciones({ userId }) {
  const [matches, setMatches] = useState([])
  const [matchPredictions, setMatchPredictions] = useState({})
  const [groupStandings, setGroupStandings] = useState({})
  const [groupPredPoints, setGroupPredPoints] = useState({})
  const [loading, setLoading] = useState(true)
  const [selectedPhase, setSelectedPhase] = useState('Fase de Grupos')
  const [expandedGroups, setExpandedGroups] = useState({}) 
  
  // const userId = 1; // Passed via props
  const phases = ['Fase de Grupos', '16avos', 'Octavos', 'Cuartos', 'Semifinal', 'Final']

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/v1/matches/`).then(res => res.json()),
      fetch(`${API_BASE}/api/v1/predictions/user/${userId}`).then(res => res.json()),
      fetch(`${API_BASE}/api/v1/group-predictions/user/${userId}`).then(res => res.json())
    ]).then(([matchesData, predictionsData, groupPredsData]) => {
        setMatches(matchesData)
        
        const mp = {};
        if (Array.isArray(predictionsData)) {
          predictionsData.forEach(p => {
            mp[p.match_id] = { home: p.score_home_predicted, away: p.score_away_predicted, saved: true };
          });
        }
        setMatchPredictions(mp);

        const gs = {};
        const gpPts = {};
        if (Array.isArray(groupPredsData)) {
          groupPredsData.forEach(gp => {
            gs[gp.group_name] = [gp.pos1_team, gp.pos2_team, gp.pos3_team, gp.pos4_team];
            gpPts[gp.group_name] = gp.points_earned;
          });
        }
        setGroupStandings(gs);
        setGroupPredPoints(gpPts);
        
        setLoading(false)
    }).catch(err => { console.error(err); setLoading(false) })
  }, [])

  const toggleGroup = (groupName) => {
    setExpandedGroups(prev => ({ ...prev, [groupName]: !prev[groupName] }))
  }

  const updateScore = (matchId, team, increment) => {
    setMatchPredictions(prev => {
      const current = prev[matchId] || { home: 0, away: 0, saved: false };
      const currentVal = current[team] === '' ? 0 : parseInt(current[team]);
      const newVal = Math.max(0, currentVal + increment);
      return {
        ...prev,
        [matchId]: { ...current, [team]: newVal, saved: false }
      };
    });
  }

  const saveMatchPrediction = (matchId) => {
    const p = matchPredictions[matchId];
    if (!p) return;
    fetch(`${API_BASE}/api/v1/predictions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, match_id: matchId, score_home_predicted: p.home, score_away_predicted: p.away })
    }).then(res => {
      if (res.ok) setMatchPredictions(prev => ({ ...prev, [matchId]: { ...prev[matchId], saved: true }}));
    })
  }

  if (loading) return <p style={{textAlign: 'center'}}>Cargando predicciones...</p>

  let filteredMatches = matches.filter(m => selectedPhase === 'Fase de Grupos' ? m.phase.startsWith('Grupo') : m.phase === selectedPhase)
  
  const groupedMatches = filteredMatches.reduce((acc, match) => {
    if (!acc[match.phase]) acc[match.phase] = [];
    acc[match.phase].push(match);
    return acc;
  }, {});

  const sortedGroups = Object.keys(groupedMatches).sort();
  
  // Progress Bar calculation
  const totalMatches = matches.filter(m => !m.isPlaceholder).length;
  const predictedCount = Object.values(matchPredictions).filter(p => p.saved).length;
  const progressPercent = totalMatches > 0 ? Math.round((predictedCount / totalMatches) * 100) : 0;

  return (
    <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
      <h2 className="section-title">Hacer Predicciones</h2>
      
      <div className="progress-container">
        <div className="progress-fill" style={{ width: `${progressPercent}%` }}></div>
      </div>
      <div className="progress-text">Progreso: {predictedCount} / {totalMatches} partidos ({progressPercent}%)</div>

      <div className="phase-selector">
        {phases.map(phase => (
          <button key={phase} onClick={() => setSelectedPhase(phase)} className={selectedPhase === phase ? 'active' : ''}>
            {phase}
          </button>
        ))}
      </div>

      {sortedGroups.length === 0 ? (
         <p style={{ textAlign: 'center', marginTop: '2rem' }}>No hay partidos cargados.</p>
      ) : (
        sortedGroups.map(groupName => {
          const isExpanded = expandedGroups[groupName] || false;
          
          const validMatches = groupedMatches[groupName].filter(m => !m.isPlaceholder);
          const defaultTeams = Array.from(new Set(validMatches.flatMap(m => [m.team_home, m.team_away]))).slice(0, 4);
          const currentStandings = groupStandings[groupName] || defaultTeams;
          const pointsEarned = groupPredPoints[groupName];

          return (
            <div key={groupName} className="group-header-card" style={{ marginBottom: '1rem', background: '#f8fafc', borderRadius: '8px', padding: '0 1rem', border: '1px solid #e2e8f0' }}>
              <h3 onClick={() => toggleGroup(groupName)}
                style={{ color: '#1e293b', fontSize: '1.25rem', padding: '1rem 0', margin: '0', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', userSelect: 'none' }}>
                <span>{groupName}</span>
                <motion.span animate={{ rotate: isExpanded ? 180 : 0 }} style={{ fontSize: '0.9rem', color: '#64748b' }}>▼</motion.span>
              </h3>
              
              <AnimatePresence>
              {isExpanded && (
                <motion.div 
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  style={{ overflow: 'hidden' }}
                >
                  <div style={{ paddingBottom: '1rem', paddingTop: '0.5rem' }}>
                  
                  {currentStandings.length === 4 && (
                    <div className="simulated-table-card" style={{ background: 'var(--simulated-bg)', borderRadius: '8px', padding: '1rem', marginBottom: '1.5rem' }}>
                      <h4 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: 'var(--text-color)', textAlign: 'center', textTransform: 'uppercase', letterSpacing: '1px' }}>Posiciones Simuladas</h4>
                      
                      {pointsEarned !== undefined && pointsEarned !== null && (
                         <div style={{ textAlign: 'center', marginBottom: '1rem', color: '#15803d', fontWeight: 'bold' }}>
                            ¡Obtuviste {pointsEarned} puntos en este grupo!
                         </div>
                      )}

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {(() => {
                          const stats = {};
                          defaultTeams.forEach(t => stats[t] = { pts: 0, gf: 0, gc: 0 });

                          groupedMatches[groupName].forEach(match => {
                            const p = matchPredictions[match.id];
                            if (p && p.home !== '' && p.away !== '' && p.home !== undefined && p.away !== undefined) {
                              const hScore = parseInt(p.home);
                              const aScore = parseInt(p.away);
                              
                              stats[match.team_home].gf += hScore;
                              stats[match.team_home].gc += aScore;
                              stats[match.team_away].gf += aScore;
                              stats[match.team_away].gc += hScore;

                              if (hScore > aScore) stats[match.team_home].pts += 3;
                              else if (hScore < aScore) stats[match.team_away].pts += 3;
                              else {
                                stats[match.team_home].pts += 1;
                                stats[match.team_away].pts += 1;
                              }
                            }
                          });

                          const sortedTeams = defaultTeams.slice().sort((a, b) => {
                            if (stats[b].pts !== stats[a].pts) return stats[b].pts - stats[a].pts;
                            const gdA = stats[a].gf - stats[a].gc;
                            const gdB = stats[b].gf - stats[b].gc;
                            if (gdB !== gdA) return gdB - gdA;
                            return stats[b].gf - stats[a].gf;
                          });

                          return sortedTeams.map((team, idx) => (
                            <motion.div layout key={team} className="simulated-row" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#fff', padding: '0.5rem 1rem', borderRadius: '4px', border: '1px solid #cbd5e1' }}>
                              <span style={{ fontWeight: 'bold', color: '#64748b', width: '20px' }}>{idx + 1}º</span>
                              <TeamConBandera team={team} textColor="#334155" />
                              <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: '#64748b', minWidth: '80px', justifyContent: 'flex-end' }}>
                                <span><b>{stats[team].pts}</b> pts</span>
                                <span>{stats[team].gf - stats[team].gc > 0 ? '+' : ''}{stats[team].gf - stats[team].gc} dif</span>
                              </div>
                            </motion.div>
                          ));
                        })()}
                      </div>
                      <p style={{ fontSize: '0.8rem', color: '#64748b', textAlign: 'center', marginTop: '1rem', fontStyle: 'italic' }}>
                        Las posiciones se calculan automáticamente según los resultados.
                      </p>
                    </div>
                  )}

                  <h4 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: 'var(--text-color)', textAlign: 'center', borderBottom: '1px solid var(--card-border)', paddingBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Partidos</h4>

                  <ul className="match-list" style={{ marginTop: '0' }}>
                    {groupedMatches[groupName].map(match => {
                      const p = matchPredictions[match.id] || { home: 0, away: 0, saved: false };
                      let dateFormatted = "Fecha no definida";
                      if (match.match_date) {
                        const utcDateStr = match.match_date.endsWith('Z') ? match.match_date : `${match.match_date}Z`;
                        dateFormatted = new Date(utcDateStr).toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires', weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
                      }

                      const btnStyle = { width: '36px', height: '36px', borderRadius: '50%', border: 'none', background: '#e2e8f0', color: '#334155', fontSize: '1.2rem', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', userSelect: 'none' };
                      const scoreStyle = { width: '30px', textAlign: 'center', fontSize: '1.3rem', fontWeight: 'bold', color: '#0f172a' };

                      return (
                        <li key={match.id} className="match-card">
                          <div className="match-date">📅 {dateFormatted}</div>
                          
                          <div className="match-teams" style={{ marginBottom: '1.5rem' }}>
                            <TeamConBandera team={match.team_home} textColor="#334155" isAway={false} />
                            <span className="vs-text">VS</span>
                            <TeamConBandera team={match.team_away} textColor="#334155" isAway={true} />
                          </div>
                          
                          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '2rem', marginBottom: '0.5rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <button style={btnStyle} onClick={() => updateScore(match.id, 'home', -1)}>-</button>
                              <span style={scoreStyle}>{p.home === '' ? 0 : p.home}</span>
                              <button style={btnStyle} onClick={() => updateScore(match.id, 'home', 1)}>+</button>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <button style={btnStyle} onClick={() => updateScore(match.id, 'away', -1)}>-</button>
                              <span style={scoreStyle}>{p.away === '' ? 0 : p.away}</span>
                              <button style={btnStyle} onClick={() => updateScore(match.id, 'away', 1)}>+</button>
                            </div>
                          </div>

                          <motion.button 
                            whileTap={{ scale: 0.95 }}
                            onClick={() => saveMatchPrediction(match.id)} 
                            disabled={p.saved || p.home === '' || p.away === ''}
                            style={{ width: '100%', marginTop: '1rem', background: p.saved ? 'var(--accent-color)' : 'var(--primary-color)', color: '#fff', padding: '0.6rem', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer', opacity: (p.home === '' || p.away === '') ? 0.5 : 1 }}>
                            {p.saved ? '✓ Guardado' : 'Guardar Resultado'}
                          </motion.button>
                        </li>
                      )
                    })}
                  </ul>
                  </div>
                </motion.div>
              )}
              </AnimatePresence>
            </div>
          )
        })
      )}
    </motion.div>
  )
}

function Ranking() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/api/v1/users/ranking`)
      .then(res => res.json())
      .then(data => { setUsers(data); setLoading(false) })
      .catch(err => { console.error(err); setLoading(false) })
  }, [])

  if (loading) return <p style={{textAlign: 'center'}}>Cargando ranking...</p>

  return (
    <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
      <h2 className="section-title">Ranking Global</h2>
      <div style={{ overflowX: 'auto' }}>
        <table className="ranking-table">
          <thead>
            <tr>
              <th>Pos.</th>
              <th>Usuario</th>
              <th style={{ textAlign: 'center' }}>Puntos</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user, index) => (
              <tr key={user.id}>
                <td style={{ fontWeight: 'bold', width: '15%' }}>#{index + 1}</td>
                <td style={{ wordBreak: 'break-word', maxWidth: '200px' }}>{user.username}</td>
                <td style={{ fontWeight: 'bold', color: 'var(--primary-color)', textAlign: 'center', width: '20%' }}>{user.total_points}</td>
              </tr>
            ))}
            {users.length === 0 && (<tr><td colSpan="3" style={{ padding: '1rem', textAlign: 'center' }}>No hay usuarios.</td></tr>)}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}

function App() {
  const [activeTab, setActiveTab] = useState('predicciones')
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [user, setUser] = useState(null)

  useEffect(() => {
    const savedUser = localStorage.getItem('prode_user');
    if (savedUser) setUser(JSON.parse(savedUser));
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setIsDarkMode(true);
      document.body.setAttribute('data-theme', 'dark');
    }
  }, [])

  const toggleTheme = () => {
    setIsDarkMode(prev => {
      const newVal = !prev;
      document.body.setAttribute('data-theme', newVal ? 'dark' : 'light');
      localStorage.setItem('theme', newVal ? 'dark' : 'light');
      return newVal;
    })
  }

  const handleLoginSuccess = async (credentialResponse) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/google-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: credentialResponse.credential })
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
        localStorage.setItem('prode_user', JSON.stringify(data.user));
      } else {
        const errData = await res.json().catch(() => ({}));
        alert("Error al iniciar sesión con el servidor: " + (errData.detail || res.statusText));
      }
    } catch (err) {
      console.error(err);
      alert("Error de conexión al iniciar sesión.");
    }
  }

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('prode_user');
  }

  const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "279991018948-85nrnpicnd0unba94tpimrt10qleqirn.apps.googleusercontent.com";

  if (!user) {
    return (
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        <main className="main-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '1rem' }}>
          <div className="auth-box" style={{ textAlign: 'center', width: '100%', maxWidth: '400px' }}>
            <h1 className="main-title" style={{ marginBottom: '1rem' }}>🏆 Prode Mundial</h1>
            <p style={{ marginBottom: '2rem', color: 'var(--text-muted)' }}>Inicia sesión con tu cuenta de Google para participar y asegurar que tus predicciones sean únicas.</p>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <GoogleLogin
                onSuccess={handleLoginSuccess}
                onError={() => alert('Fallo en el inicio de sesión')}
                useOneTap
              />
            </div>
          </div>
        </main>
      </GoogleOAuthProvider>
    )
  }

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <main className="main-container">
        <div className="header-top">
          <h1 className="main-title">🏆 Prode</h1>
          <div style={{ display: 'flex', gap: '0.8rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>{user.username}</span>
            <button className="theme-toggle" onClick={toggleTheme}>
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <button onClick={handleLogout} style={{ background: 'transparent', border: 'none', color: 'var(--primary-color)', cursor: 'pointer', fontSize: '0.8rem' }}>Salir</button>
          </div>
        </div>
        
        <AnimatePresence mode='wait'>
          {activeTab === 'fixture' && <Fixture key="fixture" userId={user.id} />}
          {activeTab === 'predicciones' && <Predicciones key="predicciones" userId={user.id} />}
          {activeTab === 'ranking' && <Ranking key="ranking" />}
        </AnimatePresence>

        <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />
      </main>
    </GoogleOAuthProvider>
  )
}

export default App
