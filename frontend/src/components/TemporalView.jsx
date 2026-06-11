import React, { useState, useEffect } from 'react';
import PlotlyComponent from 'react-plotly.js';
import { getTemporalData } from '../api';

const Plot = PlotlyComponent.default || PlotlyComponent;

const COLOR_LINEAS = {
  "Roja": "#C0392B", "Amarilla": "#D4A017", "Verde": "#1A8C4E",
  "Azul": "#1565C0", "Naranja": "#C05621", "Celeste": "#0E7490",
  "Blanca": "#94A3B8", "Café": "#7C4D33", "Plateada": "#64748B",
  "Dorada": "#B8860B", "Morada": "#6D28D9",
};

const layoutBase = {
  paper_bgcolor: '#161B27',
  plot_bgcolor: '#161B27',
  font: { color: '#E2E8F0', family: "'Inter', sans-serif", size: 12 },
  margin: { l: 50, r: 20, t: 30, b: 50 },
  xaxis: { gridcolor: '#2D3748', linecolor: '#2D3748' },
  yaxis: { gridcolor: '#2D3748', linecolor: '#2D3748' },
};

const TemporalView = ({ filters, config }) => {
  const [data, setData] = useState({ hourly: [], daily: [], dow: [] });

  useEffect(() => {
    getTemporalData(filters).then(setData).catch(console.error);
  }, [filters]);

  const lineasDisponibles = new Set();
  data.hourly.forEach(row => Object.keys(row).forEach(k => { if (k !== 'hora' && k !== 'dia_semana') lineasDisponibles.add(k); }));
  data.dow.forEach(row => Object.keys(row).forEach(k => { if (k !== 'hora' && k !== 'dia_semana') lineasDisponibles.add(k); }));
  const lineasActivas = filters.lineas.filter(l => lineasDisponibles.has(l));

  const hourlyTraces = lineasActivas.map(linea => ({
    x: data.hourly.map(d => d.hora),
    y: data.hourly.map(d => d[linea] || 0),
    name: linea, type: 'scatter', mode: 'lines',
    line: { color: COLOR_LINEAS[linea] || '#3B82F6', width: 2 }
  }));

  const dailyTraces = [
    {
      x: data.daily.map(d => d.fecha),
      y: data.daily.map(d => d.pasajeros),
      name: 'Diario', type: 'scatter', mode: 'lines',
      line: { color: '#2D3748', width: 1 },
      fill: 'tozeroy', fillcolor: 'rgba(59,130,246,0.06)'
    },
    {
      x: data.daily.map(d => d.fecha),
      y: data.daily.map(d => d.rolling7),
      name: 'Media móvil 7d', type: 'scatter', mode: 'lines',
      line: { color: '#3B82F6', width: 2 }
    }
  ];

  const dowTraces = lineasActivas.map(linea => ({
    x: data.dow.map(d => d.dia_semana),
    y: data.dow.map(d => d[linea] || 0),
    name: linea, type: 'bar',
    marker: { color: COLOR_LINEAS[linea] || '#3B82F6' }
  }));

  const subTitle = { fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontWeight: 500 };

  return (
    <div className="panel">
      <h2 className="section-title">Análisis Temporal de Pasajeros</h2>

      <div className="flex gap-4 mb-4">
        <div style={{flex: 1}}>
          <h3 style={subTitle}>Perfil de demanda por hora del día</h3>
          <Plot key="temporal-hourly" data={hourlyTraces}
            layout={{ ...layoutBase, xaxis: { ...layoutBase.xaxis, title: "Hora", tickmode: 'linear', dtick: 1 }, yaxis: { ...layoutBase.yaxis, title: "Pasajeros promedio" }, height: 340, legend: { x: 0, y: 1 } }}
            useResizeHandler={true} style={{ width: '100%', height: '340px' }} />
        </div>
        <div style={{flex: 1}}>
          <h3 style={subTitle}>Evolución diaria de pasajeros</h3>
          <Plot key="temporal-daily" data={dailyTraces}
            layout={{ ...layoutBase, xaxis: { ...layoutBase.xaxis, title: "Fecha", type: 'date' }, yaxis: { ...layoutBase.yaxis, title: "Pasajeros" }, height: 340, legend: { x: 0, y: 1 } }}
            useResizeHandler={true} style={{ width: '100%', height: '340px' }} />
        </div>
      </div>

      <div style={{marginTop: '1.5rem'}}>
        <h3 style={subTitle}>Demanda promedio por día de la semana</h3>
        <Plot key="temporal-dow" data={dowTraces}
          layout={{ ...layoutBase, xaxis: { ...layoutBase.xaxis, title: "Día de la semana", type: 'category', categoryorder: 'array', categoryarray: config.dias_orden }, yaxis: { ...layoutBase.yaxis, title: "Pasajeros promedio" }, height: 340, barmode: 'group', legend: { orientation: 'h', y: -0.2 } }}
          useResizeHandler={true} style={{ width: '100%', height: '340px' }} />
      </div>
    </div>
  );
};

export default TemporalView;
