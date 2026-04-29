import React, { useState, useEffect } from 'react';
import PlotlyComponent from 'react-plotly.js';
import { getTemporalData } from '../api';

const Plot = PlotlyComponent.default || PlotlyComponent;

const COLOR_LINEAS = {
  "Roja": "#E63946", "Amarilla": "#FFB703", "Verde": "#2DC653",
  "Azul": "#0077B6", "Naranja": "#FB8500", "Celeste": "#48CAE4",
  "Blanca": "#CED4DA", "Café": "#8B5E3C", "Plateada": "#ADB5BD",
  "Dorada": "#D4AF37", "Morada": "#7209B7",
};

const TemporalView = ({ filters, config }) => {
  const [data, setData] = useState({ hourly: [], daily: [], dow: [] });

  useEffect(() => {
    getTemporalData(filters).then(setData).catch(console.error);
  }, [filters]);

  // Format data for Plotly
  const hourlyTraces = filters.lineas.map(linea => ({
    x: data.hourly.map(d => d.hora),
    y: data.hourly.map(d => d[linea] || 0),
    name: linea,
    type: 'scatter',
    mode: 'lines',
    line: { color: COLOR_LINEAS[linea] || '#00B4FF', width: 2 }
  }));

  const dailyTraces = [
    {
      x: data.daily.map(d => d.fecha),
      y: data.daily.map(d => d.pasajeros),
      name: 'Diario',
      type: 'scatter',
      mode: 'lines',
      line: { color: '#1E3A5F', width: 1 },
      fill: 'tozeroy',
      fillcolor: 'rgba(0,100,180,0.1)'
    },
    {
      x: data.daily.map(d => d.fecha),
      y: data.daily.map(d => d.rolling7),
      name: 'Media móvil 7d',
      type: 'scatter',
      mode: 'lines',
      line: { color: '#00B4FF', width: 2.5 }
    }
  ];

  const dowTraces = filters.lineas.map(linea => ({
    x: data.dow.map(d => d.dia_semana),
    y: data.dow.map(d => d[linea] || 0),
    name: linea,
    type: 'bar',
    marker: { color: COLOR_LINEAS[linea] || '#00B4FF' }
  }));

  const layoutBase = {
    paper_bgcolor: '#111827',
    plot_bgcolor: '#111827',
    font: { color: '#E8EAF0', family: "'Barlow', sans-serif" },
    margin: { l: 40, r: 20, t: 30, b: 40 },
    xaxis: { gridcolor: '#1E3A5F' },
    yaxis: { gridcolor: '#1E3A5F' }
  };

  return (
    <div className="panel">
      <h2 className="section-title">Análisis Temporal de Pasajeros</h2>
      
      <div className="flex gap-4 mb-4">
        <div style={{flex: 1}}>
          <h3 style={{fontSize: '0.95rem', marginBottom: '0.5rem', color: 'var(--text-light)'}}>Perfil de demanda por hora del día</h3>
          <Plot
            data={hourlyTraces}
            layout={{ ...layoutBase, height: 350, legend: { x: 0, y: 1 } }}
            useResizeHandler={true}
            style={{ width: '100%', height: '350px' }}
          />
        </div>
        <div style={{flex: 1}}>
          <h3 style={{fontSize: '0.95rem', marginBottom: '0.5rem', color: 'var(--text-light)'}}>Evolución diaria de pasajeros</h3>
          <Plot
            data={dailyTraces}
            layout={{ ...layoutBase, height: 350, legend: { x: 0, y: 1 } }}
            useResizeHandler={true}
            style={{ width: '100%', height: '350px' }}
          />
        </div>
      </div>
      
      <div style={{marginTop: '2rem'}}>
        <h3 style={{fontSize: '0.95rem', marginBottom: '0.5rem', color: 'var(--text-light)'}}>Demanda promedio por día de la semana</h3>
        <Plot
          data={dowTraces}
          layout={{ ...layoutBase, height: 350, barmode: 'group', legend: { orientation: 'h', y: -0.2 } }}
          useResizeHandler={true}
          style={{ width: '100%', height: '350px' }}
        />
      </div>
    </div>
  );
};

export default TemporalView;
