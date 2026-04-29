import React, { useState, useEffect } from 'react';
import PlotlyComponent from 'react-plotly.js';
import { getPrediction } from '../api';

const Plot = PlotlyComponent.default || PlotlyComponent;

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
    if (!data || data.error) return <div style={{padding: '2rem'}}>{data?.error || 'Sin datos'}</div>;

    const traces = [];
    
    // Histórico
    traces.push({
      x: data.history.map(d => d.fecha),
      y: data.history.map(d => d.pasajeros),
      mode: 'lines+markers',
      name: 'Histórico',
      line: { color: '#00B4FF', width: 2 },
      marker: { size: 3 }
    });

    if (data.method === 'prophet') {
      // Predicción Prophet
      traces.push({
        x: data.prediction.map(d => d.fecha),
        y: data.prediction.map(d => d.yhat),
        mode: 'lines',
        name: 'Predicción',
        line: { color: '#FFB703', width: 2.5, dash: 'dash' }
      });
      
      // Intervalo de confianza
      const x = data.prediction.map(d => d.fecha);
      const xRev = [...x].reverse();
      const yUpper = data.prediction.map(d => d.yhat_upper);
      const yLower = [...data.prediction.map(d => d.yhat_lower)].reverse();
      
      traces.push({
        x: [...x, ...xRev],
        y: [...yUpper, ...yLower],
        fill: 'toself',
        fillcolor: 'rgba(255,183,3,0.1)',
        line: { color: 'rgba(0,0,0,0)' },
        name: 'Intervalo 95%'
      });
    } else {
      // Linear
      traces.push({
        x: data.prediction.map(d => d.fecha),
        y: data.prediction.map(d => d.yhat),
        mode: 'lines',
        name: 'Proyección (Lineal)',
        line: { color: '#FFB703', width: 2.5, dash: 'dash' }
      });
    }

    return (
      <Plot
        data={traces}
        layout={{
          paper_bgcolor: '#111827',
          plot_bgcolor: '#111827',
          font: { color: '#E8EAF0', family: "'Barlow', sans-serif" },
          margin: { l: 40, r: 20, t: 20, b: 40 },
          xaxis: { gridcolor: '#1E3A5F' },
          yaxis: { gridcolor: '#1E3A5F', title: 'Pasajeros' },
          legend: { x: 0, y: 1 },
          height: 400
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '400px' }}
      />
    );
  };

  return (
    <div className="panel">
      <h2 className="section-title">Predicción de Demanda — Próximos {diasPred} días</h2>
      
      <div className="flex gap-4 mb-4 items-center">
        <div>
          <label className="form-label" style={{fontSize: '0.85rem'}}>Línea a predecir</label>
          <select 
            value={linea} 
            onChange={e => setLinea(e.target.value)}
            style={{
              background: 'var(--bg-dark)', color: 'var(--text-light)', 
              border: '1px solid var(--panel-border)', padding: '0.4rem 0.8rem', borderRadius: '6px'
            }}
          >
            {filters.lineas.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <div style={{flex: 1, maxWidth: '300px'}}>
          <label className="form-label" style={{fontSize: '0.85rem'}}>Días a predecir: {diasPred}</label>
          <input 
            type="range" 
            min="7" max="60" 
            value={diasPred} 
            onChange={e => setDiasPred(parseInt(e.target.value))} 
          />
        </div>
      </div>

      <div style={{position: 'relative', minHeight: '400px'}}>
        {loading && <div style={{position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'var(--glass-bg)', zIndex: 10, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>Calculando predicción...</div>}
        {renderPlot()}
      </div>

      {data && !data.error && data.kpi && (
        <div className="flex gap-4 mt-4" style={{borderTop: '1px solid var(--panel-border)', paddingTop: '1rem'}}>
          <div style={{flex: 1}}>
            <p style={{fontSize: '0.85rem', color: 'var(--text-muted)'}}>Total proyectado</p>
            <p style={{fontFamily: 'Space Mono', fontSize: '1.5rem', color: 'var(--primary)'}}>{(data.kpi.total/1000).toFixed(1)}K</p>
          </div>
          <div style={{flex: 1}}>
            <p style={{fontSize: '0.85rem', color: 'var(--text-muted)'}}>Promedio diario</p>
            <p style={{fontFamily: 'Space Mono', fontSize: '1.5rem', color: 'var(--primary)'}}>{(data.kpi.promedio/1000).toFixed(1)}K</p>
          </div>
          <div style={{flex: 1}}>
            <p style={{fontSize: '0.85rem', color: 'var(--text-muted)'}}>Pico proyectado</p>
            <p style={{fontFamily: 'Space Mono', fontSize: '1.5rem', color: 'var(--primary)'}}>{(data.kpi.pico/1000).toFixed(1)}K</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictView;
