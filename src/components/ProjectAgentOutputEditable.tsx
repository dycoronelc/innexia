/**
 * Envolturas editables para cada sección del agente (Estrategia, Roadmap, Números, Riesgos, Veredicto).
 * Cada una muestra la vista en tarjetas + botón Editar que abre un diálogo con formulario.
 * Al guardar se llama al API correspondiente y onSaved() para refrescar datos.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Alert,
  IconButton,
  Grid,
  Divider,
} from '@mui/material';
import { Edit as EditIcon, Save as SaveIcon, Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import {
  EstrategiaComercialCards,
  RoadmapCards,
  AnalisisNumericosCards,
  RiesgosCards,
  VeredictoCards,
} from './ProjectAgentOutputCards';
import { agentOutputService } from '../services/api';

// --- Helpers para arrays en formularios (una línea por ítem) ---
function linesToArray(s: string): string[] {
  return (s || '').split('\n').map((x) => x.trim()).filter(Boolean);
}
function arrayToLines(arr: unknown[]): string {
  return Array.isArray(arr) ? arr.map(String).join('\n') : '';
}

// --- Estrategia Comercial ---
export const EstrategiaComercialEditable: React.FC<{
  data?: Record<string, unknown>;
  projectId: number;
  token: string;
  onSaved: () => void;
}> = ({ data, projectId, token, onSaved }) => {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    tamano_mercado: '',
    crecimiento_anual: '',
    competidores_principales: '',
    ventaja_competitiva: '',
    modelo_precios: '',
    justificacion_precios: '',
    descuentos: '',
    canales_marketing: '',
    presupuesto_mensual: '',
    kpis: '',
    proceso_ventas: '',
    ciclo_venta: '',
    tasa_conversion: '',
  });

  useEffect(() => {
    if (!data || !open) return;
    const am = (data.analisis_mercado || {}) as Record<string, unknown>;
    const ep = (data.estrategia_precios || {}) as Record<string, unknown>;
    const em = (data.estrategia_marketing || {}) as Record<string, unknown>;
    const ev = (data.estrategia_ventas || {}) as Record<string, unknown>;
    setForm({
      tamano_mercado: String(am.tamano_mercado ?? ''),
      crecimiento_anual: String(am.crecimiento_anual ?? ''),
      competidores_principales: arrayToLines((am.competidores_principales as unknown[]) || []),
      ventaja_competitiva: String(am.ventaja_competitiva ?? ''),
      modelo_precios: String(ep.modelo ?? ''),
      justificacion_precios: String(ep.justificacion ?? ''),
      descuentos: arrayToLines((ep.descuentos as unknown[]) || []),
      canales_marketing: arrayToLines((em.canales_principales as unknown[]) || []),
      presupuesto_mensual: String(em.presupuesto_mensual ?? ''),
      kpis: arrayToLines((em.kpis as unknown[]) || []),
      proceso_ventas: String(ev.proceso ?? ''),
      ciclo_venta: String(ev.ciclo_venta_estimado ?? ''),
      tasa_conversion: String(ev.tasa_conversion_objetivo ?? ''),
    });
  }, [data, open]);

  const handleSave = async () => {
    setError('');
    setSaving(true);
    try {
      const payload = {
        analisis_mercado: {
          tamano_mercado: form.tamano_mercado,
          crecimiento_anual: form.crecimiento_anual,
          competidores_principales: linesToArray(form.competidores_principales),
          ventaja_competitiva: form.ventaja_competitiva,
        },
        estrategia_precios: {
          modelo: form.modelo_precios,
          justificacion: form.justificacion_precios,
          descuentos: linesToArray(form.descuentos),
        },
        estrategia_marketing: {
          canales_principales: linesToArray(form.canales_marketing),
          presupuesto_mensual: form.presupuesto_mensual ? Number(form.presupuesto_mensual) : undefined,
          kpis: linesToArray(form.kpis),
        },
        estrategia_ventas: {
          proceso: form.proceso_ventas,
          ciclo_venta_estimado: form.ciclo_venta,
          tasa_conversion_objetivo: form.tasa_conversion,
        },
      };
      const res = await agentOutputService.updateEstrategiaComercial(projectId, payload, token);
      if (res.status === 'success') {
        setOpen(false);
        onSaved();
      } else {
        setError((res as { error?: string }).error || 'Error al guardar');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
        <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setOpen(true)} size="small">
          Editar
        </Button>
      </Box>
      <EstrategiaComercialCards data={data} />
      <Dialog open={open} onClose={() => !saving && setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Editar estrategia comercial</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
          <Grid container spacing={2} sx={{ pt: 1 }}>
            <Grid item xs={12}><Typography variant="subtitle2" color="primary">Análisis de mercado</Typography></Grid>
            <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Tamaño mercado" value={form.tamano_mercado} onChange={(e) => setForm({ ...form, tamano_mercado: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Crecimiento anual" value={form.crecimiento_anual} onChange={(e) => setForm({ ...form, crecimiento_anual: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth size="small" multiline rows={2} label="Competidores (uno por línea)" value={form.competidores_principales} onChange={(e) => setForm({ ...form, competidores_principales: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth size="small" label="Ventaja competitiva" value={form.ventaja_competitiva} onChange={(e) => setForm({ ...form, ventaja_competitiva: e.target.value })} /></Grid>
            <Grid item xs={12}><Divider /><Typography variant="subtitle2" color="primary" sx={{ mt: 1 }}>Estrategia de precios</Typography></Grid>
            <Grid item xs={12}><TextField fullWidth size="small" label="Modelo" value={form.modelo_precios} onChange={(e) => setForm({ ...form, modelo_precios: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth size="small" multiline rows={2} label="Justificación" value={form.justificacion_precios} onChange={(e) => setForm({ ...form, justificacion_precios: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth size="small" multiline rows={2} label="Descuentos (uno por línea)" value={form.descuentos} onChange={(e) => setForm({ ...form, descuentos: e.target.value })} /></Grid>
            <Grid item xs={12}><Divider /><Typography variant="subtitle2" color="primary" sx={{ mt: 1 }}>Estrategia de marketing</Typography></Grid>
            <Grid item xs={12}><TextField fullWidth size="small" multiline rows={2} label="Canales (uno por línea)" value={form.canales_marketing} onChange={(e) => setForm({ ...form, canales_marketing: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField fullWidth size="small" type="number" label="Presupuesto mensual" value={form.presupuesto_mensual} onChange={(e) => setForm({ ...form, presupuesto_mensual: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth size="small" multiline rows={2} label="KPIs (uno por línea)" value={form.kpis} onChange={(e) => setForm({ ...form, kpis: e.target.value })} /></Grid>
            <Grid item xs={12}><Divider /><Typography variant="subtitle2" color="primary" sx={{ mt: 1 }}>Estrategia de ventas</Typography></Grid>
            <Grid item xs={12}><TextField fullWidth size="small" label="Proceso" value={form.proceso_ventas} onChange={(e) => setForm({ ...form, proceso_ventas: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Ciclo de venta estimado" value={form.ciclo_venta} onChange={(e) => setForm({ ...form, ciclo_venta: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Tasa conversión objetivo" value={form.tasa_conversion} onChange={(e) => setForm({ ...form, tasa_conversion: e.target.value })} /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={saving}>Cancelar</Button>
          <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSave} disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// --- Roadmap ---
type FaseForm = { fase: string; duracion_meses: string; hitos: string; recursos: string };
export const RoadmapEditable: React.FC<{
  data?: Record<string, unknown>;
  projectId: number;
  token: string;
  onSaved: () => void;
}> = ({ data, projectId, token, onSaved }) => {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [cronogramaTotal, setCronogramaTotal] = useState('');
  const [fases, setFases] = useState<FaseForm[]>([]);

  useEffect(() => {
    if (!data || !open) return;
    const total = data.cronograma_total_meses;
    const fasesData = (data.fases || []) as Array<Record<string, unknown>>;
    setCronogramaTotal(String(total ?? ''));
    setFases(
      fasesData.length
        ? fasesData.map((f) => ({
            fase: String(f.fase ?? ''),
            duracion_meses: String(f.duracion_meses ?? ''),
            hitos: arrayToLines((f.hitos as unknown[]) || []),
            recursos: arrayToLines((f.recursos_necesarios as unknown[]) || []),
          }))
        : [{ fase: '', duracion_meses: '', hitos: '', recursos: '' }]
    );
  }, [data, open]);

  const addFase = () => setFases((prev) => [...prev, { fase: '', duracion_meses: '', hitos: '', recursos: '' }]);
  const removeFase = (i: number) => setFases((prev) => prev.filter((_, idx) => idx !== i));
  const updateFase = (i: number, field: keyof FaseForm, value: string) =>
    setFases((prev) => prev.map((f, idx) => (idx === i ? { ...f, [field]: value } : f)));

  const handleSave = async () => {
    setError('');
    setSaving(true);
    try {
      const payload = {
        cronograma_total_meses: cronogramaTotal ? parseInt(cronogramaTotal, 10) : undefined,
        fases: fases
          .filter((f) => f.fase.trim())
          .map((f) => ({
            fase: f.fase,
            duracion_meses: f.duracion_meses ? parseInt(f.duracion_meses, 10) : 0,
            hitos: linesToArray(f.hitos),
            recursos_necesarios: linesToArray(f.recursos),
          })),
      };
      const res = await agentOutputService.updateRoadmap(projectId, payload, token);
      if (res.status === 'success') {
        setOpen(false);
        onSaved();
      } else {
        setError((res as { error?: string }).error || 'Error al guardar');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
        <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setOpen(true)} size="small">
          Editar
        </Button>
      </Box>
      <RoadmapCards data={data} />
      <Dialog open={open} onClose={() => !saving && setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Editar roadmap</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
          <TextField fullWidth size="small" type="number" label="Cronograma total (meses)" value={cronogramaTotal} onChange={(e) => setCronogramaTotal(e.target.value)} sx={{ mb: 2 }} />
          {fases.map((f, i) => (
            <Box key={i} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2">Fase {i + 1}</Typography>
                <IconButton size="small" onClick={() => removeFase(i)} disabled={fases.length <= 1}><DeleteIcon /></IconButton>
              </Box>
              <Grid container spacing={1}>
                <Grid item xs={12} sm={4}><TextField fullWidth size="small" label="Nombre fase" value={f.fase} onChange={(e) => updateFase(i, 'fase', e.target.value)} /></Grid>
                <Grid item xs={12} sm={4}><TextField fullWidth size="small" type="number" label="Duración (meses)" value={f.duracion_meses} onChange={(e) => updateFase(i, 'duracion_meses', e.target.value)} /></Grid>
                <Grid item xs={12}><TextField fullWidth size="small" multiline rows={2} label="Hitos (uno por línea)" value={f.hitos} onChange={(e) => updateFase(i, 'hitos', e.target.value)} /></Grid>
                <Grid item xs={12}><TextField fullWidth size="small" multiline rows={2} label="Recursos necesarios (uno por línea)" value={f.recursos} onChange={(e) => updateFase(i, 'recursos', e.target.value)} /></Grid>
              </Grid>
            </Box>
          ))}
          <Button startIcon={<AddIcon />} onClick={addFase} size="small">Añadir fase</Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={saving}>Cancelar</Button>
          <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSave} disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// --- Análisis financiero (Números) ---
type ProyeccionForm = { ano: string; ingresos: string; costos: string; utilidad_neta: string; clientes_estimados: string };
type DesgloseForm = { concepto: string; monto: string };
export const AnalisisFinancieroEditable: React.FC<{
  data?: Record<string, unknown>;
  projectId: number;
  token: string;
  onSaved: () => void;
}> = ({ data, projectId, token, onSaved }) => {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [totalInversion, setTotalInversion] = useState('');
  const [desglose, setDesglose] = useState<DesgloseForm[]>([]);
  const [proyecciones, setProyecciones] = useState<ProyeccionForm[]>([]);
  const [roi, setRoi] = useState('');
  const [puntoEquilibrio, setPuntoEquilibrio] = useState('');
  const [ltvCac, setLtvCac] = useState('');
  const [margenBruto, setMargenBruto] = useState('');
  const [viabilidad, setViabilidad] = useState('');

  useEffect(() => {
    if (!data || !open) return;
    const inv = (data.inversion_inicial || {}) as Record<string, unknown>;
    setTotalInversion(String(inv.total ?? ''));
    const d = (inv.desglose || []) as Array<Record<string, unknown>>;
    setDesglose(d.length ? d.map((x) => ({ concepto: String(x.concepto ?? ''), monto: String(x.monto ?? '') })) : [{ concepto: '', monto: '' }]);
    const proy = (data.proyecciones_3_anos || []) as Array<Record<string, unknown>>;
    setProyecciones(
      proy.length
        ? proy.map((p) => ({
            ano: String(p.ano ?? ''),
            ingresos: String(p.ingresos ?? ''),
            costos: String(p.costos ?? ''),
            utilidad_neta: String(p.utilidad_neta ?? ''),
            clientes_estimados: String(p.clientes_estimados ?? ''),
          }))
        : [{ ano: '1', ingresos: '', costos: '', utilidad_neta: '', clientes_estimados: '' }]
    );
    const m = (data.metricas_clave || {}) as Record<string, unknown>;
    setRoi(String(m.roi_3_anos ?? ''));
    setPuntoEquilibrio(String(m.punto_equilibrio_meses ?? ''));
    setLtvCac(String(m.ltv_cac_ratio ?? ''));
    setMargenBruto(String(m.margen_bruto ?? ''));
    setViabilidad(String(data.viabilidad_financiera ?? ''));
  }, [data, open]);

  const addDesglose = () => setDesglose((prev) => [...prev, { concepto: '', monto: '' }]);
  const removeDesglose = (i: number) => setDesglose((prev) => prev.filter((_, idx) => idx !== i));
  const updateDesglose = (i: number, field: keyof DesgloseForm, value: string) =>
    setDesglose((prev) => prev.map((d, idx) => (idx === i ? { ...d, [field]: value } : d)));
  const addProyeccion = () =>
    setProyecciones((prev) => [...prev, { ano: String(prev.length + 1), ingresos: '', costos: '', utilidad_neta: '', clientes_estimados: '' }]);
  const removeProyeccion = (i: number) => setProyecciones((prev) => prev.filter((_, idx) => idx !== i));
  const updateProyeccion = (i: number, field: keyof ProyeccionForm, value: string) =>
    setProyecciones((prev) => prev.map((p, idx) => (idx === i ? { ...p, [field]: value } : p)));

  const handleSave = async () => {
    setError('');
    setSaving(true);
    try {
      const payload = {
        inversion_inicial: {
          total: totalInversion ? Number(totalInversion) : undefined,
          desglose: desglose.filter((d) => d.concepto.trim()).map((d) => ({ concepto: d.concepto, monto: Number(d.monto) || 0 })),
        },
        proyecciones_3_anos: proyecciones
          .filter((p) => p.ano.trim())
          .map((p) => ({
            ano: Number(p.ano) || 0,
            ingresos: Number(p.ingresos) || 0,
            costos: Number(p.costos) || 0,
            utilidad_neta: Number(p.utilidad_neta) || 0,
            clientes_estimados: Number(p.clientes_estimados) || 0,
          })),
        metricas_clave: {
          roi_3_anos: roi || undefined,
          punto_equilibrio_meses: puntoEquilibrio ? Number(puntoEquilibrio) : undefined,
          ltv_cac_ratio: ltvCac || undefined,
          margen_bruto: margenBruto || undefined,
        },
        viabilidad_financiera: viabilidad || undefined,
      };
      const res = await agentOutputService.updateAnalisisFinanciero(projectId, payload, token);
      if (res.status === 'success') {
        setOpen(false);
        onSaved();
      } else {
        setError((res as { error?: string }).error || 'Error al guardar');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
        <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setOpen(true)} size="small">
          Editar
        </Button>
      </Box>
      <AnalisisNumericosCards data={data} />
      <Dialog open={open} onClose={() => !saving && setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Editar análisis financiero</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
          <Typography variant="subtitle2" color="primary" sx={{ mt: 1 }}>Inversión inicial</Typography>
          <TextField fullWidth size="small" type="number" label="Total" value={totalInversion} onChange={(e) => setTotalInversion(e.target.value)} sx={{ mb: 1 }} />
          {desglose.map((d, i) => (
            <Box key={i} sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField size="small" label="Concepto" value={d.concepto} onChange={(e) => updateDesglose(i, 'concepto', e.target.value)} sx={{ flex: 2 }} />
              <TextField size="small" type="number" label="Monto" value={d.monto} onChange={(e) => updateDesglose(i, 'monto', e.target.value)} sx={{ flex: 1 }} />
              <IconButton size="small" onClick={() => removeDesglose(i)}><DeleteIcon /></IconButton>
            </Box>
          ))}
          <Button startIcon={<AddIcon />} onClick={addDesglose} size="small">Añadir concepto</Button>
          <Typography variant="subtitle2" color="primary" sx={{ mt: 2 }}>Proyecciones 3 años</Typography>
          {proyecciones.map((p, i) => (
            <Box key={i} sx={{ p: 1.5, border: '1px solid', borderColor: 'divider', borderRadius: 1, mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}><IconButton size="small" onClick={() => removeProyeccion(i)}><DeleteIcon /></IconButton></Box>
              <Grid container spacing={1}>
                <Grid item xs={6} sm={2}><TextField fullWidth size="small" type="number" label="Año" value={p.ano} onChange={(e) => updateProyeccion(i, 'ano', e.target.value)} /></Grid>
                <Grid item xs={6} sm={2}><TextField fullWidth size="small" type="number" label="Ingresos" value={p.ingresos} onChange={(e) => updateProyeccion(i, 'ingresos', e.target.value)} /></Grid>
                <Grid item xs={6} sm={2}><TextField fullWidth size="small" type="number" label="Costos" value={p.costos} onChange={(e) => updateProyeccion(i, 'costos', e.target.value)} /></Grid>
                <Grid item xs={6} sm={2}><TextField fullWidth size="small" type="number" label="Utilidad neta" value={p.utilidad_neta} onChange={(e) => updateProyeccion(i, 'utilidad_neta', e.target.value)} /></Grid>
                <Grid item xs={6} sm={2}><TextField fullWidth size="small" type="number" label="Clientes" value={p.clientes_estimados} onChange={(e) => updateProyeccion(i, 'clientes_estimados', e.target.value)} /></Grid>
              </Grid>
            </Box>
          ))}
          <Button startIcon={<AddIcon />} onClick={addProyeccion} size="small">Añadir año</Button>
          <Typography variant="subtitle2" color="primary" sx={{ mt: 2 }}>Métricas clave</Typography>
          <Grid container spacing={1}>
            <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="ROI 3 años" value={roi} onChange={(e) => setRoi(e.target.value)} /></Grid>
            <Grid item xs={12} sm={6}><TextField fullWidth size="small" type="number" label="Punto equilibrio (meses)" value={puntoEquilibrio} onChange={(e) => setPuntoEquilibrio(e.target.value)} /></Grid>
            <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="LTV/CAC" value={ltvCac} onChange={(e) => setLtvCac(e.target.value)} /></Grid>
            <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Margen bruto" value={margenBruto} onChange={(e) => setMargenBruto(e.target.value)} /></Grid>
            <Grid item xs={12}><TextField fullWidth size="small" label="Viabilidad financiera" value={viabilidad} onChange={(e) => setViabilidad(e.target.value)} placeholder="ej. ALTA" /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={saving}>Cancelar</Button>
          <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSave} disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// --- Riesgos ---
type RiesgoForm = { categoria: string; riesgo: string; probabilidad: string; impacto: string; mitigacion: string };
export const RiesgosEditable: React.FC<{
  data?: Record<string, unknown>;
  projectId: number;
  token: string;
  onSaved: () => void;
}> = ({ data, projectId, token, onSaved }) => {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [nivelRiesgo, setNivelRiesgo] = useState('');
  const [recomendaciones, setRecomendaciones] = useState('');
  const [riesgos, setRiesgos] = useState<RiesgoForm[]>([]);

  useEffect(() => {
    if (!data || !open) return;
    setNivelRiesgo(String(data.nivel_riesgo_general ?? ''));
    setRecomendaciones(arrayToLines((data.recomendaciones as unknown[]) || []));
    const r = (data.riesgos_identificados || []) as Array<Record<string, unknown>>;
    setRiesgos(
      r.length
        ? r.map((x) => ({
            categoria: String(x.categoria ?? ''),
            riesgo: String(x.riesgo ?? ''),
            probabilidad: String(x.probabilidad ?? ''),
            impacto: String(x.impacto ?? ''),
            mitigacion: String(x.mitigacion ?? ''),
          }))
        : [{ categoria: '', riesgo: '', probabilidad: '', impacto: '', mitigacion: '' }]
    );
  }, [data, open]);

  const addRiesgo = () => setRiesgos((prev) => [...prev, { categoria: '', riesgo: '', probabilidad: '', impacto: '', mitigacion: '' }]);
  const removeRiesgo = (i: number) => setRiesgos((prev) => prev.filter((_, idx) => idx !== i));
  const updateRiesgo = (i: number, field: keyof RiesgoForm, value: string) =>
    setRiesgos((prev) => prev.map((r, idx) => (idx === i ? { ...r, [field]: value } : r)));

  const handleSave = async () => {
    setError('');
    setSaving(true);
    try {
      const payload = {
        nivel_riesgo_general: nivelRiesgo || undefined,
        recomendaciones: linesToArray(recomendaciones),
        riesgos_identificados: riesgos
          .filter((r) => r.riesgo.trim())
          .map((r) => ({
            categoria: r.categoria,
            riesgo: r.riesgo,
            probabilidad: r.probabilidad,
            impacto: r.impacto,
            mitigacion: r.mitigacion,
          })),
      };
      const res = await agentOutputService.updateAnalisisRiesgos(projectId, payload, token);
      if (res.status === 'success') {
        setOpen(false);
        onSaved();
      } else {
        setError((res as { error?: string }).error || 'Error al guardar');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
        <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setOpen(true)} size="small">
          Editar
        </Button>
      </Box>
      <RiesgosCards data={data} />
      <Dialog open={open} onClose={() => !saving && setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Editar análisis de riesgos</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
          <TextField fullWidth size="small" label="Nivel de riesgo general" value={nivelRiesgo} onChange={(e) => setNivelRiesgo(e.target.value)} placeholder="ej. MEDIO" sx={{ mb: 2 }} />
          <TextField fullWidth size="small" multiline rows={3} label="Recomendaciones (una por línea)" value={recomendaciones} onChange={(e) => setRecomendaciones(e.target.value)} sx={{ mb: 2 }} />
          {riesgos.map((r, i) => (
            <Box key={i} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}><IconButton size="small" onClick={() => removeRiesgo(i)}><DeleteIcon /></IconButton></Box>
              <Grid container spacing={1}>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Categoría" value={r.categoria} onChange={(e) => updateRiesgo(i, 'categoria', e.target.value)} /></Grid>
                <Grid item xs={12}><TextField fullWidth size="small" label="Riesgo" value={r.riesgo} onChange={(e) => updateRiesgo(i, 'riesgo', e.target.value)} /></Grid>
                <Grid item xs={12} sm={4}><TextField fullWidth size="small" label="Probabilidad" value={r.probabilidad} onChange={(e) => updateRiesgo(i, 'probabilidad', e.target.value)} placeholder="ej. MEDIA" /></Grid>
                <Grid item xs={12} sm={4}><TextField fullWidth size="small" label="Impacto" value={r.impacto} onChange={(e) => updateRiesgo(i, 'impacto', e.target.value)} placeholder="ej. ALTO" /></Grid>
                <Grid item xs={12}><TextField fullWidth size="small" multiline rows={2} label="Mitigación" value={r.mitigacion} onChange={(e) => updateRiesgo(i, 'mitigacion', e.target.value)} /></Grid>
              </Grid>
            </Box>
          ))}
          <Button startIcon={<AddIcon />} onClick={addRiesgo} size="small">Añadir riesgo</Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={saving}>Cancelar</Button>
          <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSave} disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// --- Veredicto ---
export const VeredictoEditable: React.FC<{
  data?: Record<string, unknown>;
  projectId: number;
  token: string;
  onSaved: () => void;
}> = ({ data, projectId, token, onSaved }) => {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [decision, setDecision] = useState('');
  const [puntuacion, setPuntuacion] = useState('');
  const [fortalezas, setFortalezas] = useState('');
  const [debilidades, setDebilidades] = useState('');
  const [recomendacion, setRecomendacion] = useState('');
  const [siguientePaso, setSiguientePaso] = useState('');

  useEffect(() => {
    if (!data || !open) return;
    setDecision(String(data.decision ?? ''));
    setPuntuacion(String(data.puntuacion_general ?? ''));
    setFortalezas(arrayToLines((data.fortalezas as unknown[]) || []));
    setDebilidades(arrayToLines((data.debilidades as unknown[]) || []));
    setRecomendacion(String(data.recomendacion_estrategica ?? ''));
    setSiguientePaso(String(data.siguiente_paso ?? ''));
  }, [data, open]);

  const handleSave = async () => {
    setError('');
    setSaving(true);
    try {
      const payload = {
        decision: decision || undefined,
        puntuacion_general: puntuacion ? Number(puntuacion) : undefined,
        fortalezas: linesToArray(fortalezas),
        debilidades: linesToArray(debilidades),
        recomendacion_estrategica: recomendacion || undefined,
        siguiente_paso: siguientePaso || undefined,
      };
      const res = await agentOutputService.updateVeredicto(projectId, payload, token);
      if (res.status === 'success') {
        setOpen(false);
        onSaved();
      } else {
        setError((res as { error?: string }).error || 'Error al guardar');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
        <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setOpen(true)} size="small">
          Editar
        </Button>
      </Box>
      <VeredictoCards data={data} />
      <Dialog open={open} onClose={() => !saving && setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Editar veredicto</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
          <TextField fullWidth size="small" label="Decisión" value={decision} onChange={(e) => setDecision(e.target.value)} placeholder="ej. POSITIVO" sx={{ mb: 1 }} />
          <TextField fullWidth size="small" type="number" inputProps={{ step: 0.1, min: 0, max: 10 }} label="Puntuación general (0-10)" value={puntuacion} onChange={(e) => setPuntuacion(e.target.value)} sx={{ mb: 1 }} />
          <TextField fullWidth size="small" multiline rows={3} label="Fortalezas (una por línea)" value={fortalezas} onChange={(e) => setFortalezas(e.target.value)} sx={{ mb: 1 }} />
          <TextField fullWidth size="small" multiline rows={3} label="Debilidades (una por línea)" value={debilidades} onChange={(e) => setDebilidades(e.target.value)} sx={{ mb: 1 }} />
          <TextField fullWidth size="small" multiline rows={3} label="Recomendación estratégica" value={recomendacion} onChange={(e) => setRecomendacion(e.target.value)} sx={{ mb: 1 }} />
          <TextField fullWidth size="small" multiline rows={2} label="Siguiente paso" value={siguientePaso} onChange={(e) => setSiguientePaso(e.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={saving}>Cancelar</Button>
          <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSave} disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
