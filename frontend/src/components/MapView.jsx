import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getMapData } from '../api';

const COLOR_LINEAS = {
  "Roja": "#E63946", "Amarilla": "#FFB703", "Verde": "#2DC653",
  "Azul": "#0077B6", "Naranja": "#FB8500", "Celeste": "#48CAE4",
  "Blanca": "#CED4DA", "Café": "#8B5E3C", "Plateada": "#ADB5BD",
  "Dorada": "#D4AF37", "Morada": "#7209B7",
};

const lineas_rutas = {
  "Roja":     [[-16.530,-68.119],[-16.520,-68.115],[-16.504,-68.113],[-16.497,-68.115]],
  "Amarilla": [[-16.508,-68.131],[-16.503,-68.138],[-16.499,-68.143],[-16.494,-68.148]],
  "Verde":    [[-16.507,-68.123],[-16.513,-68.127],[-16.520,-68.130],[-16.535,-68.125]],
  "Azul":     [[-16.490,-68.120],[-16.495,-68.118],[-16.500,-68.116],[-16.505,-68.114]],
  "Naranja":  [[-16.478,-68.154],[-16.485,-68.148],[-16.497,-68.136],[-16.530,-68.115]],
  "Celeste":  [[-16.472,-68.165],[-16.480,-68.158],[-16.493,-68.142],[-16.508,-68.110]],
  "Blanca":   [[-16.550,-68.105],[-16.542,-68.108],[-16.535,-68.112],[-16.528,-68.118]],
  "Café":     [[-16.555,-68.101],[-16.545,-68.104],[-16.510,-68.109],[-16.502,-68.107]],
  "Plateada": [[-16.490,-68.145],[-16.480,-68.150],[-16.474,-68.156],[-16.501,-68.133]],
  "Dorada":   [[-16.465,-68.170],[-16.470,-68.162],[-16.475,-68.155],[-16.483,-68.147]],
  "Morada":   [[-16.538,-68.108],[-16.525,-68.106],[-16.518,-68.110],[-16.510,-68.112]],
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
