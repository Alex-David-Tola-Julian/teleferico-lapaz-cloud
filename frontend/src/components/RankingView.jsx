import React, { useState, useEffect } from 'react';
import { getRanking } from '../api';

const COLOR_LINEAS = {
  "Roja": "#E63946", "Amarilla": "#FFB703", "Verde": "#2DC653",
  "Azul": "#0077B6", "Naranja": "#FB8500", "Celeste": "#48CAE4",
  "Blanca": "#CED4DA", "Café": "#8B5E3C", "Plateada": "#ADB5BD",
  "Dorada": "#D4AF37", "Morada": "#7209B7",
};

const RankingView = ({ filters }) => {
  const [data, setData] = useState({ top: [], bottom: [], max_total: 0 });

  useEffect(() => {
    getRanking(filters).then(setData).catch(console.error);
  }, [filters]);

  const renderList = (items, isTop) => {
    return items.map((row, i) => {
      const color = COLOR_LINEAS[row.linea] || (isTop ? "#00B4FF" : "#7A8FA6");
      const pct = (row.total / data.max_total) * 100;
      
      const bgGradient = isTop 
        ? `linear-gradient(90deg, rgba(0,180,255,0.06) 0%, transparent 100%)`
        : `linear-gradient(90deg, rgba(122,143,166,0.06) 0%, transparent 100%)`;

      return (
        <div key={`${row.estacion}-${row.linea}`} style={{
          margin: '8px 0', padding: '10px 14px',
          background: bgGradient,
          borderLeft: `3px solid ${color}`, borderRadius: '4px'
        }}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div>
              <span style={{fontFamily: 'Space Mono', color, fontSize: '0.78rem'}}>#{i + 1 < 10 ? `0${i+1}` : i+1}</span>
              <span style={{fontSize: '0.92rem', fontWeight: 600, marginLeft: '8px'}}>{row.estacion}</span>
              <span style={{fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '6px'}}>· {row.linea}</span>
            </div>
            <span style={{fontFamily: 'Space Mono', color: isTop ? '#00B4FF' : '#7A8FA6', fontSize: '0.85rem'}}>
              {(row.total/1000).toFixed(0)}K
            </span>
          </div>
          <div style={{marginTop: '5px', background: '#1E3A5F', borderRadius: '3px', height: '4px'}}>
            <div style={{width: `${pct}%`, height: '4px', background: color, borderRadius: '3px'}}></div>
          </div>
        </div>
      );
    });
  };

  return (
    <div className="panel">
      <h2 className="section-title">Ranking de Estaciones por Flujo de Pasajeros</h2>
      
      <div className="flex gap-4">
        <div style={{flex: 1}}>
          <h3 style={{fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-light)'}}>🏆 Top 10 — Más concurridas</h3>
          {renderList(data.top, true)}
        </div>
        <div style={{flex: 1}}>
          <h3 style={{fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-light)'}}>📉 Bottom 10 — Menos concurridas</h3>
          {renderList(data.bottom, false)}
        </div>
      </div>
    </div>
  );
};

export default RankingView;
