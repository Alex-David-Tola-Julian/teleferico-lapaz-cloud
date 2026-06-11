import React, { useState, useEffect } from 'react';
import PlotlyComponent from 'react-plotly.js';
import { getPrediction } from '../api';

const Plot = PlotlyComponent.default || PlotlyComponent;

const plotLayout = {
  paper_bgcolor: '#161B27',
  plot_bgcolor: '#161B27',
  font: { color: '#E2E8F0', family: "'Inter', sans-serif", size: 12 },
  margin: { l: 50, r: 20, t: 20, b: 50 },
  xaxis: { gridcolor: '#2D3748', linecolor: '#2D3748' },
  yaxis: { gridcolor: '#2D3748', linecolor: '#2D3748', title: 'Pasajeros' },
  legend: { x: 0, y: 1, bgcolor: 'rgba(0,0,0,0)' },
  height: 400,
};

const PredictView = ({ filters, config }) => {
  const [data, setData] = useState(null);
  const [linea, setLinea] = useState(filters.lineas[0] || config.lineas_disp[0]);
  const [diasPred, setDiasPred] = useState(30);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getPrediction(filters, linea, diasPred).then(res => {
      setData(res);
      setLoading(false);
    }).catch(e => {
      console.error(e);
      setLoading(false);
    });
  }, [filters, linea, diasPred]);

  const renderPlot = () => {
    if (!data || data.error) return <div style={{padding: '2rem', color: 'var(--text-muted)'}}>{data?.error || 'Sin datos'}</div>;

    const traces = [];
    traces.push({
      x: data.history.map(d => d.fecha),
      y: data.history.map(d => d.pasajeros),
      mode: 'lines',
      name: 'Histórico',
      line: { color: '#3B82F6', width: 2 },
    });

    if (data.method === 'prophet') {
      traces.push({
        x: data.prediction.map(d => d.fecha),
        y: data.prediction.map(d => d.yhat),
        mode: 'lines',
        name: 'Predicción',
        line: { color: '#F59E0B', width: 2, dash: 'dash' }
      });
      const x = data.prediction.map(d => d.fecha);
      const xRev = [...x].reverse();
      const yUpper = data.prediction.map(d => d.yhat_upper);
      const yLower = [...data.prediction.map(d => d.yhat_lower)].reverse();
      traces.push({
        x: [...x, ...xRev],
        y: [...yUpper, ...yLower],
        fill: 'toself',
        fillcolor: 'rgba(245,158,11,0.08)',
        line: { color: 'rgba(0,0,0,0)' },
        name: 'Intervalo 95%'
      });
    } else {
      traces.push({
        x: data.prediction.map(d => d.fecha),
        y: data.prediction.map(d => d.yhat),
        mode: 'lines',
        name: 'Proyección lineal',
        line: { color: '#F59E0B', width: 2, dash: 'dash' }
      });
    }

    return (
      <Plot
        data={traces}
        layout={plotLayout}
        useResizeHandler={true}
        style={{ width: '100%', height: '400px' }}
      />
    );
  };

  const selectStyle = {
    background: 'var(--bg-dark)', color: 'var(--text-primary)',
    border: '1px solid var(--border)', padding: '0.4rem 0.75rem',
    borderRadius: '6px', fontSize: '0.85rem',
  };

  return (
    <div className="panel">
      <h2 className="section-title">Predicción de Demanda — Próximos {diasPred} días</h2>

      <div className="flex gap-4 mb-4 items-center">
        <div>
          <label className="form-label">Línea a predecir</label>
          <select value={linea} onChange={e => setLinea(e.target.value)} style={selectStyle}>
            {filters.lineas.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <div style={{flex: 1, maxWidth: '280px'}}>
          <label className="form-label">Días a predecir: {diasPred}</label>
          <input type="range" min="7" max="60" value={diasPred} onChange={e => setDiasPred(parseInt(e.target.value))} />
        </div>
      </div>

      <div style={{position: 'relative', minHeight: '400px'}}>
        {loading && (
          <div style={{position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'var(--bg-panel)', zIndex: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.9rem'}}>
            Calculando predicción...
          </div>
        )}
        {renderPlot()}
      </div>

      {data && !data.error && data.kpi && (
        <div className="flex gap-4 mt-4" style={{borderTop: '1px solid var(--border)', paddingTop: '1rem'}}>
          {[
            { label: 'Total proyectado', value: `${(data.kpi.total/1000).toFixed(1)}K` },
            { label: 'Promedio diario',  value: `${(data.kpi.promedio/1000).toFixed(1)}K` },
            { label: 'Pico proyectado',  value: `${(data.kpi.pico/1000).toFixed(1)}K` },
          ].map(kpi => (
            <div key={kpi.label} style={{flex: 1}}>
              <p style={{fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em'}}>{kpi.label}</p>
              <p style={{fontFamily: 'JetBrains Mono', fontSize: '1.4rem', color: 'var(--text-primary)', fontWeight: 700}}>{kpi.value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PredictView;
