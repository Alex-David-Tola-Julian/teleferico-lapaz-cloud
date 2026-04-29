import React from 'react';

const Sidebar = ({ config, filters, setFilters }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleLineToggle = (linea) => {
    setFilters(prev => {
      const isSelected = prev.lineas.includes(linea);
      let newLines = isSelected 
        ? prev.lineas.filter(l => l !== linea)
        : [...prev.lineas, linea];
      if (newLines.length === 0) newLines = config.lineas_disp; // don't allow empty
      return { ...prev, lineas: newLines };
    });
  };

  const handleDayToggle = (dia) => {
    setFilters(prev => {
      const isSelected = prev.dias_semana.includes(dia);
      let newDays = isSelected
        ? prev.dias_semana.filter(d => d !== dia)
        : [...prev.dias_semana, dia];
      if (newDays.length === 0) newDays = config.dias_orden; // don't allow empty
      return { ...prev, dias_semana: newDays };
    });
  };

  return (
    <aside className="sidebar">
      <div style={{ textAlign: 'center', padding: '1rem 0 1.5rem 0' }}>
        <span style={{ fontFamily: 'Space Mono', fontSize: '1.5rem', color: '#00B4FF' }}>🚡</span>
        <p style={{ fontFamily: 'Space Mono', fontSize: '0.9rem', color: '#00B4FF', margin: '0.3rem 0 0' }}>Mi Teleférico</p>
        <p style={{ fontSize: '0.72rem', color: '#7A8FA6', margin: 0 }}>Dashboard Analytics · La Paz</p>
      </div>

      <div className="mb-4">
        <label className="form-label">🗓 Rango de fechas</label>
        <div className="flex gap-4" style={{gap: '0.5rem'}}>
          <input type="date" name="fecha_inicio" value={filters.fecha_inicio} onChange={handleChange} min={config.fecha_min} max={filters.fecha_fin} />
          <input type="date" name="fecha_fin" value={filters.fecha_fin} onChange={handleChange} min={filters.fecha_inicio} max={config.fecha_max} />
        </div>
      </div>

      <div className="mb-4">
        <div className="flex justify-between items-center mb-4">
          <label className="form-label" style={{margin: 0}}>🚡 Líneas</label>
          <button className="btn" style={{padding: '0.2rem 0.5rem', fontSize: '0.7rem'}} onClick={() => setFilters(prev => ({...prev, lineas: config.lineas_disp}))}>Todo</button>
        </div>
        {config.lineas_disp.map(linea => (
          <label key={linea} className="checkbox-label">
            <input type="checkbox" checked={filters.lineas.includes(linea)} onChange={() => handleLineToggle(linea)} />
            {linea}
          </label>
        ))}
      </div>

      <div className="mb-4">
        <label className="form-label">⏰ Horario: {filters.hora_min}h - {filters.hora_max}h</label>
        <div className="flex justify-between" style={{gap: '0.5rem'}}>
          <input type="range" name="hora_min" min="5" max="22" value={filters.hora_min} onChange={handleChange} />
          <input type="range" name="hora_max" min="5" max="22" value={filters.hora_max} onChange={handleChange} />
        </div>
      </div>

      <div className="mb-4">
        <div className="flex justify-between items-center mb-4">
          <label className="form-label" style={{margin: 0}}>📅 Días de la semana</label>
          <button className="btn" style={{padding: '0.2rem 0.5rem', fontSize: '0.7rem'}} onClick={() => setFilters(prev => ({...prev, dias_semana: config.dias_orden}))}>Todo</button>
        </div>
        {config.dias_orden.map(dia => (
          <label key={dia} className="checkbox-label">
            <input type="checkbox" checked={filters.dias_semana.includes(dia)} onChange={() => handleDayToggle(dia)} />
            {dia}
          </label>
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;
