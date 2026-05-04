import React, { useState, useEffect } from 'react';
import { Map, Clock, Activity, TrendingUp, Award } from 'lucide-react';
import { getConfig, getMetrics, getCloudStatus } from './api';
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
  const [cloudStatus, setCloudStatus] = useState(null);
  const [apiLatency, setApiLatency] = useState(0);
  const [openPanels, setOpenPanels] = useState({
    resumenCloud: false,
  });

  const escenarios = {
    laboral: {
      label: 'Hora pico laboral',
      hora_min: 7,
      hora_max: 9,
      dias_semana: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
    },
    finde: {
      label: 'Fin de semana',
      hora_min: 10,
      hora_max: 20,
      dias_semana: ['Sábado', 'Domingo'],
    },
    saturada: {
      label: 'Línea más saturada',
      hora_min: 6,
      hora_max: 21,
      dias_semana: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
    },
  };

  useEffect(() => {
    getConfig().then(data => {
      setApiLatency(data._latency_ms || 0);
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

    getCloudStatus().then(setCloudStatus).catch(e => console.error('Error loading cloud status', e));
  }, []);

  useEffect(() => {
    if (filters) {
      getMetrics(filters).then(setMetrics).catch(e => console.error("Error loading metrics", e));
    }
  }, [filters]);

  if (!config || !filters) return <div style={{padding: '2rem', color: '#E8EAF0'}}>Cargando...</div>;

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

  const togglePanel = (key) => {
    setOpenPanels(prev => ({ ...prev, [key]: !prev[key] }));
  };

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

        <section className="panel cloud-panel">
          <button className="collapse-btn" onClick={() => togglePanel('resumenCloud')}>
            Resumen Cloud y Demo {openPanels.resumenCloud ? '▾' : '▸'}
          </button>
          {openPanels.resumenCloud && (
            <>
              <h3 className="section-title" style={{marginTop: '0.9rem'}}>Estado Cloud</h3>
              <div className="cloud-grid">
                <div><strong>Fuente:</strong> {cloudStatus?.data_source === 'supabase' ? 'Supabase' : 'CSV local'}</div>
                <div><strong>Total registros:</strong> {(cloudStatus?.total_registros || 0).toLocaleString()}</div>
                <div><strong>Última fecha:</strong> {cloudStatus?.ultima_fecha || '—'}</div>
                <div><strong>Tiempo respuesta API:</strong> {apiLatency || cloudStatus?._latency_ms || 0} ms</div>
              </div>

              <h3 className="section-title">KPI de cobertura</h3>
              <div className="cloud-grid">
                <div><strong>Rango analizado:</strong> {rangoDias} días</div>
                <div><strong>N° líneas activas:</strong> {(metrics.lineas_activas || 0).toLocaleString()}</div>
                <div><strong>N° estaciones:</strong> {(metrics.estaciones_activas || 0).toLocaleString()}</div>
                <div><strong>Registros filtrados:</strong> {(metrics.registros_filtrados || 0).toLocaleString()}</div>
              </div>

              <h3 className="section-title">Narrativa automática</h3>
              <p className="narrative-text">{narrativa}</p>

              <h3 className="section-title">Modo demo</h3>
              <div className="demo-buttons">
                <button className="btn" onClick={() => aplicarEscenario('laboral')}>{escenarios.laboral.label}</button>
                <button className="btn" onClick={() => aplicarEscenario('finde')}>{escenarios.finde.label}</button>
                <button className="btn" onClick={() => aplicarEscenario('saturada')}>{escenarios.saturada.label}</button>
              </div>
            </>
          )}
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
