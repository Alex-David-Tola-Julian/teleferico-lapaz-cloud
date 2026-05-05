import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getMapData } from '../api';

const COLOR_LINEAS = {
  "Roja": "#E63946", "Amarilla": "#FFB703", "Verde": "#2DC653",
  "Azul": "#0077B6", "Naranja": "#FB8500", "Celeste": "#48CAE4",
  "Blanca": "#F1FAEE", "Café": "#8B5E3C", "Plateada": "#ADB5BD",
  "Dorada": "#D4AF37", "Morada": "#7209B7",
};

const lineas_rutas = {
  "Roja":     [[-16.4913, -68.1384], [-16.4958, -68.1491], [-16.4908, -68.1633]],
  "Amarilla": [[-16.5292, -68.1189], [-16.5130, -68.1302], [-16.5134, -68.1403], [-16.5166, -68.1554]],
  "Verde":    [[-16.5292, -68.1189], [-16.5299, -68.1114], [-16.5375, -68.1065], [-16.5381, -68.0877]],
  "Azul":     [[-16.4908, -68.1633], [-16.4950, -68.1680], [-16.4990, -68.1720], [-16.4938, -68.1932], [-16.4862, -68.2045]],
  "Naranja":  [[-16.4913, -68.1384], [-16.4916, -68.1293], [-16.4880, -68.1250], [-16.4965, -68.1182]],
  "Celeste":  [[-16.5292, -68.1189], [-16.5147, -68.1261], [-16.5050, -68.1300], [-16.5029, -68.1331]],
  "Blanca":   [[-16.4965, -68.1182], [-16.5022, -68.1170], [-16.5065, -68.1189], [-16.5147, -68.1261]],
  "Café":     [[-16.5022, -68.1170], [-16.4950, -68.1080]],
  "Plateada": [[-16.4908, -68.1633], [-16.5136, -68.1652], [-16.5166, -68.1554]],
  "Dorada":   [[-16.4800, -68.1400], [-16.4862, -68.2045]],
  "Morada":   [[-16.5020, -68.1350], [-16.5136, -68.1652], [-16.5050, -68.1666]],
};

const MapView = ({ filters, config }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    getMapData(filters).then(setData).catch(e => console.error("Error map", e));
  }, [filters]);

  return (
    <div className="panel">
      <h2 className="section-title">Mapa de Flujo de Pasajeros — La Paz</h2>
      
      <div className="flex gap-4">
        <div style={{ flex: 3 }}>
          <MapContainer center={[-16.505, -68.128]} zoom={13} style={{ height: '500px', width: '100%', borderRadius: '12px', border: '1px solid var(--panel-border)' }}>
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
            />
            
            {/* Draw Routes */}
            {Object.entries(lineas_rutas).map(([linea, coords]) => {
              if (filters.lineas.includes(linea)) {
                return (
                  <Polyline key={linea} positions={coords} color={COLOR_LINEAS[linea] || '#FFF'} weight={4} opacity={0.85} />
                );
              }
              return null;
            })}

            {/* Draw Stations */}
            {data.map((row, i) => {
              const color = COLOR_LINEAS[row.linea] || "#FFFFFF";
              const sat = row.saturacion;
              const radio = 6 + Math.floor(sat / 15);
              const fillColor = sat > 75 ? "#E63946" : sat > 50 ? "#FFB703" : "#2DC653";
              
              return (
                <CircleMarker 
                  key={i} 
                  center={[row.latitud, row.longitud]} 
                  radius={radio}
                  color={color}
                  fillColor={fillColor}
                  fillOpacity={0.85}
                  weight={2}
                >
                  <Popup>
                    <div style={{fontFamily: 'monospace', fontSize: '12px', minWidth: '160px', color: '#333'}}>
                      <b style={{color}}>{row.estacion}</b><br/>
                      Línea <b>{row.linea}</b><br/>
                      Pasajeros: <b>{Math.round(row.pasajeros).toLocaleString()}</b><br/>
                      Saturación: <b style={{color: fillColor}}>{sat.toFixed(1)}%</b>
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </MapContainer>
        </div>
        
        <div style={{ flex: 1, padding: '1rem', background: 'var(--bg-dark)', borderRadius: '12px', border: '1px solid var(--panel-border)' }}>
          <h3 style={{marginBottom: '1rem', color: 'var(--text-light)'}}>Leyenda de líneas</h3>
          {filters.lineas.map(linea => (
            <div key={linea} style={{display: 'flex', alignItems: 'center', gap: '8px', margin: '8px 0'}}>
              <div style={{width: '14px', height: '14px', borderRadius: '50%', background: COLOR_LINEAS[linea] || '#FFF', flexShrink: 0}}></div>
              <div>
                <div style={{fontSize: '0.85rem', fontWeight: 600}}>{linea}</div>
              </div>
            </div>
          ))}
          
          <hr style={{borderColor: 'var(--panel-border)', margin: '1rem 0'}} />
          <h3 style={{marginBottom: '0.5rem', color: 'var(--text-light)'}}>Saturación</h3>
          <div style={{fontSize: '0.85rem', lineHeight: 2}}>
            <span style={{color: '#2DC653'}}>●</span> Verde — &lt;50%<br/>
            <span style={{color: '#FFB703'}}>●</span> Amarillo — 50-75%<br/>
            <span style={{color: '#E63946'}}>●</span> Rojo — &gt;75%
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapView;
