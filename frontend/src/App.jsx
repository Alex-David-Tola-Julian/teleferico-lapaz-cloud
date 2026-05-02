import React, { useState, useEffect } from 'react';
import { Map, Clock, Activity, TrendingUp, Award } from 'lucide-react';
import { getConfig, getMetrics } from './api';
import MapView from './components/MapView';
import TemporalView from './components/TemporalView';
import HeatmapView from './components/HeatmapView';
import PredictView from './components/PredictView';
import RankingView from './components/RankingView';
import Sidebar from './components/Sidebar';

function App() {
  const [config, setConfig] = useState(null);
  const [filters, setFilters] = useState(null);
  const [metrics, setMetrics] = useState({ total_pax: 0, prom_diario: 0, sat_prom: 0, linea_top: '—' });
  const [activeTab, setActiveTab] = useState('map');

  useEffect(() => {
    getConfig().then(data => {
      setConfig(data);
      // Default filters
      const endDate = new Date(data.fecha_max);
      const startDate = new Date(endDate);
      startDate.setDate(startDate.getDate() - 30);
      
      setFilters({
        fecha_inicio: startDate.toISOString().split('T')[0],
        fecha_fin: data.fecha_max,
        lineas: data.lineas_disp,
        hora_min: 5,
        hora_max: 22,
        dias_semana: data.dias_orden
      });
    }).catch(e => console.error("Error loading config", e));
  }, []);

  useEffect(() => {
    if (filters) {
      getMetrics(filters).then(setMetrics).catch(e => console.error("Error loading metrics", e));
    }
  }, [filters]);

  if (!config || !filters) return <div style={{padding: '2rem', color: '#E8EAF0'}}>Cargando...</div>;

  return (
    <div className="flex">
      <Sidebar config={config} filters={filters} setFilters={setFilters} />
      
      <main className="main-content flex-1">
        <header className="hero-header">
          <h1 className="hero-title">🚡 Mi Teleférico · Análisis de datos</h1>
          <p className="hero-subtitle">Sistema de Monitoreo y Predicción de Pasajeros — La Paz, Bolivia</p>
          <span className="hero-badge">GRUPO 19 · COMPUTACIÓN EN LA NUBE · UMSA 2026</span>
          <span className={`source-badge ${config.data_source === 'supabase' ? 'supabase' : 'csv'}`}>
            {config.data_source === 'supabase' ? 'Usamos Supabase' : 'Usamos datos de CSV'}
          </span>
        </header>

        <section className="metrics-grid">
          <div className="metric-card">
            <p className="metric-value">{(metrics.total_pax / 1000000).toFixed(2)}M</p>
            <p className="metric-label">Total Pasajeros</p>
            <p className="metric-delta">↑ período seleccionado</p>
          </div>
          <div className="metric-card">
            <p className="metric-value">{(metrics.prom_diario / 1000).toFixed(1)}K</p>
            <p className="metric-label">Promedio Diario</p>
            <p className="metric-delta">por día</p>
          </div>
          <div className="metric-card">
            <p className="metric-value" style={{color: metrics.sat_prom > 75 ? '#E63946' : metrics.sat_prom > 50 ? '#FFB703' : '#2DC653'}}>
              {metrics.sat_prom.toFixed(1)}%
            </p>
            <p className="metric-label">Saturación Promedio</p>
            <p className="metric-delta">de capacidad</p>
          </div>
          <div className="metric-card">
            <p className="metric-value" style={{fontSize: '1.5rem'}}>{metrics.linea_top}</p>
            <p className="metric-label">Línea Más Demandada</p>
            <p className="metric-delta">mayor flujo de pasajeros</p>
          </div>
        </section>

        <div className="tabs-container">
          <button className={`flex items-center gap-4 tab-btn ${activeTab === 'map' ? 'active' : ''}`} onClick={() => setActiveTab('map')}><Map size={18}/> Mapa Interactivo</button>
          <button className={`flex items-center gap-4 tab-btn ${activeTab === 'temporal' ? 'active' : ''}`} onClick={() => setActiveTab('temporal')}><TrendingUp size={18}/> Análisis Temporal</button>
          <button className={`flex items-center gap-4 tab-btn ${activeTab === 'heatmap' ? 'active' : ''}`} onClick={() => setActiveTab('heatmap')}><Activity size={18}/> Heatmap de Demanda</button>
          <button className={`flex items-center gap-4 tab-btn ${activeTab === 'predict' ? 'active' : ''}`} onClick={() => setActiveTab('predict')}><Clock size={18}/> Predicción</button>
          <button className={`flex items-center gap-4 tab-btn ${activeTab === 'ranking' ? 'active' : ''}`} onClick={() => setActiveTab('ranking')}><Award size={18}/> Ranking Estaciones</button>
        </div>

        <div className="tab-content">
          {activeTab === 'map' && <MapView filters={filters} config={config} />}
          {activeTab === 'temporal' && <TemporalView filters={filters} config={config} />}
          {activeTab === 'heatmap' && <HeatmapView filters={filters} config={config} />}
          {activeTab === 'predict' && <PredictView filters={filters} config={config} />}
          {activeTab === 'ranking' && <RankingView filters={filters} config={config} />}
        </div>
      </main>
    </div>
  );
}

export default App;
