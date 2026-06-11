import React, { useState, useEffect } from 'react';
import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Map, Clock, Activity, TrendingUp, Award } from 'lucide-react';
import { getConfig, getMetrics } from './api';
import MapView from './components/MapView';
import TemporalView from './components/TemporalView';
import HeatmapView from './components/HeatmapView';
import PredictView from './components/PredictView';
import RankingView from './components/RankingView';
import Sidebar from './components/Sidebar';
import TicketDashboard from './components/TicketDashboard';

function App() {
  const [filters, setFilters] = useState(null);

  const { data: config, isLoading: isLoadingConfig } = useQuery({
    queryKey: ['config'],
    queryFn: getConfig,
  });

  const { data: metrics = { total_pax: 0, prom_diario: 0, sat_prom: 0, linea_top: '—', registros_filtrados: 0, lineas_activas: 0, estaciones_activas: 0 } } = useQuery({
    queryKey: ['metrics', filters],
    queryFn: () => getMetrics(filters),
    enabled: !!filters,
  });

  useEffect(() => {
    if (config && !filters) {
      setFilters({
        fecha_inicio: config.fecha_min,
        fecha_fin: config.fecha_max,
        lineas: config.lineas_disp,
        hora_min: 5,
        hora_max: 22,
        dias_semana: config.dias_orden
      });
    }
  }, [config, filters]);

  if (isLoadingConfig || !filters) return <div style={{padding: '2rem', color: '#E8EAF0'}}>Cargando sistema...</div>;

  const navLinkClass = ({ isActive }) => `flex items-center gap-4 tab-btn ${isActive ? 'active' : ''}`;

  const handleTicketRegistrado = (registro) => {
    setFilters(prev => {
      if (!prev || !config) return prev;

      const fechasFin = [prev.fecha_fin, config.fecha_max, registro?.fecha].filter(Boolean).sort();
      return {
        ...prev,
        fecha_inicio: config.fecha_min,
        fecha_fin: fechasFin[fechasFin.length - 1],
      };
    });
  };

  return (
    <div className="flex">
      <Sidebar config={config} filters={filters} setFilters={setFilters} />
      <main className="main-content flex-1">
        <header className="hero-header">
          <h1 className="hero-title">🚡 Mi Teleférico · Análisis de datos</h1>
          <p className="hero-subtitle">Sistema de Monitoreo y Predicción de Pasajeros — La Paz, Bolivia</p>
          <span className="hero-badge">GRUPO 19 · COMPUTACIÓN EN LA NUBE · UMSA 2026</span>
          <span className={`source-badge ${config.data_source === 'supabase' ? 'supabase' : 'csv'}`} >
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

        <TicketDashboard onRegistrado={handleTicketRegistrado} />

        <div className="tabs-container">
          <NavLink to="/mapa" className={navLinkClass}><Map size={18}/> Mapa Interactivo</NavLink>
          <NavLink to="/temporal" className={navLinkClass}><TrendingUp size={18}/> Análisis Temporal</NavLink>
          <NavLink to="/heatmap" className={navLinkClass}><Activity size={18}/> Heatmap de Demanda</NavLink>
          <NavLink to="/predicciones" className={navLinkClass}><Clock size={18}/> Predicción</NavLink>
          <NavLink to="/ranking" className={navLinkClass}><Award size={18}/> Ranking Estaciones</NavLink>
        </div>

        <div className="tab-content">
          <Routes>
            <Route path="/" element={<Navigate to="/mapa" replace />} />
            <Route path="/mapa" element={<MapView filters={filters} config={config} />} />
            <Route path="/temporal" element={<TemporalView filters={filters} config={config} />} />
            <Route path="/heatmap" element={<HeatmapView filters={filters} config={config} />} />
            <Route path="/predicciones" element={<PredictView filters={filters} config={config} />} />
            <Route path="/ranking" element={<RankingView filters={filters} config={config} />} />
            <Route path="*" element={<div>Ruta no encontrada</div>} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;
