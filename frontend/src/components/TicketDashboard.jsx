import React, { useState, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Ticket, CheckCircle, AlertCircle } from 'lucide-react';
import { registrarTicket } from '../api';

const LINEAS = [
  { nombre: "Roja",     color: "#E63946", textColor: "#fff" },
  { nombre: "Amarilla", color: "#FFD700", textColor: "#1a1a2e" },
  { nombre: "Verde",    color: "#2DC653", textColor: "#fff" },
  { nombre: "Azul",     color: "#0077B6", textColor: "#fff" },
  { nombre: "Naranja",  color: "#FB8500", textColor: "#fff" },
  { nombre: "Blanca",   color: "#E8EAF0", textColor: "#1a1a2e" },
  { nombre: "Celeste",  color: "#48CAE4", textColor: "#1a1a2e" },
  { nombre: "Morada",   color: "#7B2FBE", textColor: "#fff" },
  { nombre: "Café",     color: "#8B5E3C", textColor: "#fff" },
  { nombre: "Plateada", color: "#9E9E9E", textColor: "#fff" },
];

export default function TicketDashboard({ onRegistrado }) {
  const [lineaSeleccionada, setLineaSeleccionada] = useState(null);
  const [pasajeros, setPasajeros] = useState('');
  const [estado, setEstado] = useState(null); // null | 'loading' | 'ok' | 'error'
  const [ultimoRegistro, setUltimoRegistro] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');
  const queryClient = useQueryClient();
  const timeoutRef = useRef(null);

  const linea = LINEAS.find(l => l.nombre === lineaSeleccionada);

  const handleSubmit = async () => {
    if (!lineaSeleccionada) { setEstado('error'); setErrorMsg('Selecciona una línea'); return; }
    const num = parseInt(pasajeros, 10);
    if (!num || num <= 0) { setEstado('error'); setErrorMsg('Ingresa un número válido > 0'); return; }

    setEstado('loading');
    setErrorMsg('');
    try {
      const res = await registrarTicket(lineaSeleccionada, num);
      setUltimoRegistro(res.registro);
      setHistorial(prev => [{ ...res.registro, _id: Date.now() }, ...prev].slice(0, 10));
      setEstado('ok');
      setPasajeros('');
      // Invalidar queries para que el dashboard se actualice
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
      queryClient.invalidateQueries({ queryKey: ['config'] });
      queryClient.invalidateQueries({ queryKey: ['cloudStatus'] });
      if (onRegistrado) onRegistrado(res.registro);
      // Resetear estado después de 3s
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => setEstado(null), 3500);
    } catch (e) {
      setEstado('error');
      setErrorMsg(e?.response?.data?.detail || 'Error al registrar');
    }
  };

  return (
    <div style={{
      background: '#0d1b2a',
      borderRadius: '16px',
      border: '1px solid rgba(122,143,166,0.18)',
      padding: '1.8rem',
      marginBottom: '1.5rem',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.4rem' }}>
        <div style={{
          background: 'rgba(122,143,166,0.16)',
          border: '1px solid rgba(122,143,166,0.22)',
          borderRadius: '10px', padding: '0.5rem', display: 'flex',
        }}>
          <Ticket size={22} color="#C9D4E3" />
        </div>
        <div>
          <h2 style={{ margin: 0, color: '#E8EAF0', fontSize: '1.15rem', fontWeight: 700 }}>
            Simulador de Tickets en Tiempo Real
          </h2>
          <p style={{ margin: 0, color: '#7A8FA6', fontSize: '0.78rem' }}>
            Registra pasajeros y actualiza las estadísticas al instante
          </p>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ color: '#9AA3B2', fontSize: '0.72rem', fontWeight: 600 }}>EN VIVO</span>
        </div>
      </div>

      {/* Selector de línea */}
      <p style={{ color: '#7A8FA6', fontSize: '0.82rem', margin: '0 0 0.7rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        1 · Selecciona la línea
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.4rem' }}>
        {LINEAS.map(l => (
          <button
            key={l.nombre}
            id={`ticket-linea-${l.nombre.toLowerCase()}`}
            onClick={() => setLineaSeleccionada(l.nombre)}
            style={{
              background: lineaSeleccionada === l.nombre ? l.color : 'rgba(255,255,255,0.05)',
              color: lineaSeleccionada === l.nombre ? l.textColor : '#9AA3B2',
              border: `2px solid ${lineaSeleccionada === l.nombre ? l.color : 'rgba(255,255,255,0.1)'}`,
              borderRadius: '8px',
              padding: '0.45rem 0.85rem',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              transition: 'background 0.18s ease, border-color 0.18s ease, color 0.18s ease',
            }}
          >
            {l.nombre}
          </button>
        ))}
      </div>

      {/* Input de pasajeros */}
      <p style={{ color: '#7A8FA6', fontSize: '0.82rem', margin: '0 0 0.7rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        2 · Número de pasajeros
      </p>
      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '1.4rem' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <input
            id="ticket-pasajeros-input"
            type="number"
            min="1"
            max="1000"
            value={pasajeros}
            onChange={e => setPasajeros(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
            placeholder="Ej: 5"
            style={{
              width: '100%',
              background: 'rgba(255,255,255,0.06)',
              border: `1.5px solid ${linea ? linea.color + '88' : 'rgba(255,255,255,0.12)'}`,
              borderRadius: '10px',
              padding: '0.65rem 1rem',
              color: '#E8EAF0',
              fontSize: '1.1rem',
              fontWeight: 700,
              outline: 'none',
              boxSizing: 'border-box',
              transition: 'border-color 0.2s',
            }}
          />
        </div>
        {/* Botones rápidos */}
        {[1, 5, 10, 50].map(n => (
          <button
            key={n}
            id={`ticket-quick-${n}`}
            onClick={() => setPasajeros(String(n))}
            style={{
              background: 'rgba(255,255,255,0.07)',
              border: '1px solid rgba(255,255,255,0.12)',
              borderRadius: '8px',
              color: '#9AA3B2',
              padding: '0.55rem 0.75rem',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '0.8rem',
              transition: 'all 0.15s',
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.14)'}
            onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.07)'}
          >
            +{n}
          </button>
        ))}
      </div>

      {/* Botón registrar */}
      <button
        id="ticket-registrar-btn"
        onClick={handleSubmit}
        disabled={estado === 'loading'}
        style={{
          width: '100%',
          padding: '0.85rem',
          background: linea ? linea.color : '#1F6F9D',
          color: linea ? linea.textColor : '#fff',
          border: 'none',
          borderRadius: '10px',
          fontWeight: 800,
          fontSize: '1rem',
          cursor: estado === 'loading' ? 'not-allowed' : 'pointer',
          opacity: estado === 'loading' ? 0.7 : 1,
          transition: 'all 0.2s',
          letterSpacing: '0.03em',
        }}
      >
        {estado === 'loading' ? 'Registrando...' : 'Registrar Ticket'}
      </button>

      {/* Feedback */}
      {estado === 'ok' && ultimoRegistro && (
        <div style={{
          marginTop: '1rem',
          background: 'rgba(45,198,83,0.12)',
          border: '1px solid rgba(45,198,83,0.3)',
          borderRadius: '10px',
          padding: '0.85rem 1rem',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.6rem',
        }}>
          <CheckCircle size={20} color="#2DC653" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <p style={{ margin: 0, color: '#2DC653', fontWeight: 700, fontSize: '0.9rem' }}>
              {ultimoRegistro.pasajeros} pasajero{ultimoRegistro.pasajeros > 1 ? 's' : ''} registrado{ultimoRegistro.pasajeros > 1 ? 's' : ''} en Línea {ultimoRegistro.linea}
            </p>
            <p style={{ margin: '0.2rem 0 0', color: '#7A8FA6', fontSize: '0.78rem' }}>
              {ultimoRegistro.estacion} · {ultimoRegistro.fecha} {String(ultimoRegistro.hora).padStart(2,'0')}:00 · Sat. {ultimoRegistro.saturacion}%
            </p>
          </div>
        </div>
      )}
      {estado === 'error' && (
        <div style={{
          marginTop: '1rem',
          background: 'rgba(230,57,70,0.12)',
          border: '1px solid rgba(230,57,70,0.3)',
          borderRadius: '10px',
          padding: '0.75rem 1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
        }}>
          <AlertCircle size={18} color="#E63946" />
          <p style={{ margin: 0, color: '#E63946', fontSize: '0.85rem', fontWeight: 600 }}>{errorMsg}</p>
        </div>
      )}

      {/* Historial de sesión */}
      {historial.length > 0 && (
        <div style={{ marginTop: '1.4rem' }}>
          <p style={{ color: '#7A8FA6', fontSize: '0.78rem', margin: '0 0 0.6rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Últimos registros de esta sesión
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', maxHeight: '200px', overflowY: 'auto' }}>
            {historial.map(r => {
              const l = LINEAS.find(x => x.nombre === r.linea);
              return (
                <div key={r._id} style={{
                  background: 'rgba(255,255,255,0.04)',
                  borderRadius: '8px',
                  padding: '0.45rem 0.75rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.6rem',
                  fontSize: '0.8rem',
                }}>
                  <div style={{
                    width: '10px', height: '10px', borderRadius: '50%',
                    background: l?.color || '#7A8FA6', flexShrink: 0,
                  }} />
                  <span style={{ color: '#E8EAF0', fontWeight: 600 }}>{r.linea}</span>
                  <span style={{ color: '#7A8FA6' }}>·</span>
                  <span style={{ color: '#00B4FF', fontWeight: 700 }}>{r.pasajeros} pax</span>
                  <span style={{ color: '#7A8FA6' }}>·</span>
                  <span style={{ color: '#7A8FA6' }}>{r.estacion}</span>
                  <span style={{ color: '#7A8FA6', marginLeft: 'auto' }}>{r.fecha} {String(r.hora).padStart(2,'0')}:00</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
