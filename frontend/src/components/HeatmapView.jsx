import React, { useState, useEffect } from 'react';
import PlotlyComponent from 'react-plotly.js';
import { getHeatmap } from '../api';

const Plot = PlotlyComponent.default || PlotlyComponent;

const HeatmapView = ({ filters, config }) => {
  const [data, setData] = useState({ x: [], y: [], z: [], insight: null });
  const [linea, setLinea] = useState('Todas');

  useEffect(() => {
    getHeatmap(filters, linea).then(setData).catch(console.error);
  }, [filters, linea]);

  return (
    <div className="panel">
      <div className="flex justify-between items-center">
        <h2 className="section-title" style={{margin: 0}}>Mapa de Calor — Demanda por Hora y Día</h2>
        <select 
          value={linea} 
          onChange={e => setLinea(e.target.value)}
          style={{
            background: 'var(--bg-dark)', 
            color: 'var(--text-light)', 
            border: '1px solid var(--panel-border)',
            padding: '0.4rem 0.8rem',
            borderRadius: '6px'
          }}
        >
          <option value="Todas">Todas las líneas</option>
          {filters.lineas.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>

      <div style={{marginTop: '1.5rem'}}>
        <Plot
          data={[{
            z: data.z,
            x: data.x,
            y: data.y,
            type: 'heatmap',
            colorscale: [
              [0.0, "#0A0E1A"], [0.2, "#0D3B6B"], [0.5, "#0077B6"],
              [0.75, "#FFB703"], [1.0, "#E63946"]
            ],
            hovertemplate: "<b>%{y}</b> — %{x}<br>Pasajeros: %{z:,.0f}<extra></extra>"
          }]}
          layout={{
            paper_bgcolor: '#111827',
            plot_bgcolor: '#111827',
            font: { color: '#E8EAF0', family: "'Barlow', sans-serif" },
            margin: { l: 80, r: 20, t: 30, b: 50 },
            xaxis: { title: "Hora del día", tickfont: { size: 11 } },
            yaxis: { tickfont: { size: 12 } },
            height: 400
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: '400px' }}
        />
      </div>

      {data.insight && (
        <div style={{
          background: 'rgba(0,180,255,0.08)',
          border: '1px solid rgba(0,180,255,0.25)',
          borderRadius: '10px',
          padding: '1rem 1.5rem',
          marginTop: '1rem'
        }}>
          <span style={{color: '#00B4FF', fontFamily: 'Space Mono', fontSize: '0.85rem'}}>
            💡 INSIGHT
          </span><br/>
          <span style={{fontSize: '0.95rem'}}>
            El pico máximo de demanda ocurre los <b style={{color: '#FFB703'}}>{data.insight.dia}</b> a las <b style={{color: '#FFB703'}}>{data.insight.hora.toString().padStart(2, '0')}:00h</b> con un promedio de <b style={{color: '#E63946'}}>{Math.round(data.insight.valor).toLocaleString()}</b> pasajeros.
          </span>
        </div>
      )}
    </div>
  );
};

export default HeatmapView;
