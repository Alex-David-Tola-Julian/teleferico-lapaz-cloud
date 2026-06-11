import React, { useState, useEffect } from 'react';
import { Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Map, Clock, Activity, TrendingUp, Award, Ticket } from 'lucide-react';
import { getConfig, getMetrics, getCloudStatus } from './api';
import MapView from './components/MapView';
import TemporalView from './components/TemporalView';
import HeatmapView from './components/HeatmapView';
import PredictView from './components/PredictView';
import RankingView from './components/RankingView';
import Sidebar from './components/Sidebar';
import TicketDashboard from './components/TicketDashboard';

function App() {
  const [filters, setFilters] = useState(null);
  const [openPanels, setOpenPanels] = useState({ resumenCloud: false });

  const location = useLocation();

  const escenarios = {
    laboral: { label: 'Hora pico laboral', hora_min: 7, hora_max: 9, dias_semana: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'] },
    finde: { label: 'Fin de semana', hora_min: 10, hora_max: 20, dias_semana: ['Sábado', 'Domingo'] },
    saturada: { label: 'Línea más saturada', hora_min: 6, hora_max: 21, dias_semana: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'] },
  };

  const { data: config, isLoading: isLoadingConfig } = useQuery({
    queryKey: ['config'],
    queryFn: getConfig,
  });

  const { data: cloudStatus } = useQuery({
    queryKey: ['cloudStatus'],
    queryFn: getCloudStatus,
  });

  const { data: metrics = { total_pax: 0, prom_diario: 0, sat_prom: 0, linea_top: '—', registros_filtrados: 0, lineas_activas: 0, estaciones_activas: 0 } } = useQuery({
    queryKey: ['metrics', filters],
    queryFn: () => getMetrics(filters),
    enabled: !!filters,
  });

  useEffect(() => {
    if (config && !filters) {
      const endDate = new Date(config.fecha_max);
      const startDate = new Date(endDate);
      startDate.setDate(startDate.getDate() - 30);
      setFilters({
        fecha_inicio: startDate.toISOString().split('T')[0],
        fecha_fin: config.fecha_max,
        lineas: config.lineas_disp,
        hora_min: 5,
        hora_max: 22,
        dias_semana: config.dias_orden
      });
    }
  }, [config, filters]);

  if (isLoadingConfig || !filters) return <div style={{padding: '2rem', color: '#E8EAF0'}}>Cargando sistema...</div>;

  const fechaInicio = new Date(filters.fecha_inicio);
  const fechaFin = new Date(filters.fecha_fin);
  const rangoDias = Math.max(1, Math.round((fechaFin - fechaInicio) / (1000 * 60 * 60 * 24)) + 1);
  const narrativa = metrics.registros_filtrados > 0
    ? `Pico estimado en ${metrics.linea_top} con ${metrics.sat_prom.toFixed(1)}% de saturación promedio en ${metrics.registros_filtrados.toLocaleString()} registros filtrados.`
    : 'No hay datos para los filtros actuales. Ajusta fechas, líneas u horarios para detectar picos de demanda.';

  const aplicarEscenario = (key) => {
    const esc = escenarios[key];
    if (!esc) return;
    setFilters(prev => ({
      ...prev,
      hora_min: esc.hora_min,
      hora_max: esc.hora_max,
      dias_semana: esc.dias_semana,
      lineas: key === 'saturada' && metrics.linea_top !== '—' ? [metrics.linea_top] : config.lineas_disp,
    }));
  };

  const navLinkClass = ({ isActive }) => `flex items-center gap-4 tab-btn ${isActive ? 'active' : ''}`;

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

        <section className="panel cloud-panel">
          <button className="collapse-btn" onClick={() => setOpenPanels(prev => ({ ...prev, resumenCloud: !prev.resumenCloud }))}>
            Resumen Cloud y Demo {openPanels.resumenCloud ? '▾' : '▸'}
          </button>
          {openPanels.resumenCloud && (
            <>
              <h3 className="section-title" style={{marginTop: '0.9rem'}}>Estado Cloud</h3>
              <div className="cloud-grid">
                <div><strong>Fuente:</strong> {cloudStatus?.data_source === 'supabase' ? 'Supabase' : 'CSV local'}</div>
                <div><strong>Total registros:</strong> {(cloudStatus?.total_registros || 0).toLocaleString()}</div>
                <div><strong>Última fecha:</strong> {cloudStatus?.ultima_fecha || '—'}</div>
                <div><strong>Tiempo respuesta API:</strong> {config._latency_ms || cloudStatus?._latency_ms || 0} ms</div>
              </div>
              <h3 className="section-title">KPI de cobertura</h3>
              <div className="cloud-grid">
                <div><strong>Rango analizado:</strong> {rangoDias} días</div>
                <div><strong>N° líneas activas:</strong> {(metrics.lineas_activas || 0).toLocaleString()}</div>
                <div><strong>N° estaciones:</strong> {(metrics.estaciones_activas || 0).toLocaleString()}</div>
                <div><strong>Registros filtrados:</strong> {(metrics.registros_filtrados || 0).toLocaleString()}</div>
              </div>
            </>
          )}
        </section>

        <TicketDashboard onRegistrado={() => {}} />

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
