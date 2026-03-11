import React from 'react';
import { Box, Card, CardContent, Typography, Chip, Grid, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import {
  Store as StoreIcon,
  Timeline as TimelineIcon,
  ShowChart as ChartIcon,
  Warning as WarningIcon,
  Gavel as GavelIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';

const cardSx = {
  borderRadius: 3,
  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
  border: '1px solid',
  borderColor: 'divider',
  height: '100%',
  transition: 'box-shadow 0.2s ease',
  '&:hover': { boxShadow: '0 8px 30px rgba(0,0,0,0.12)' },
};

const sectionTitleSx = { fontWeight: 700, mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 };

function renderList(items: unknown, bullet = true): React.ReactNode {
  if (!items) return null;
  const arr = Array.isArray(items) ? items : [items];
  return (
    <List dense disablePadding>
      {arr.map((item: unknown, i: number) => {
        const text = typeof item === 'object' && item !== null && 'concepto' in (item as Record<string, unknown>)
          ? `${(item as { concepto?: string }).concepto}: ${(item as { monto?: number; frecuencia?: string }).monto ?? ''} ${(item as { frecuencia?: string }).frecuencia ?? ''}`
          : String(item);
        return (
          <ListItem key={i} sx={{ py: 0.25 }} disableGutters>
            {bullet && <ListItemIcon sx={{ minWidth: 28 }}><CheckIcon sx={{ fontSize: 18 }} color="primary" /></ListItemIcon>}
            <ListItemText primary={text} primaryTypographyProps={{ variant: 'body2' }} />
          </ListItem>
        );
      })}
    </List>
  );
}

export const EstrategiaComercialCards: React.FC<{ data?: Record<string, unknown> }> = ({ data }) => {
  if (!data) return <Typography color="text.secondary">No hay datos de estrategia comercial.</Typography>;
  const analisis = (data.analisis_mercado || data) as Record<string, unknown>;
  const precios = (data.estrategia_precios || {}) as Record<string, unknown>;
  const marketing = (data.estrategia_marketing || {}) as Record<string, unknown>;
  const ventas = (data.estrategia_ventas || {}) as Record<string, unknown>;
  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Card sx={cardSx}>
          <CardContent>
            <Typography variant="h6" sx={sectionTitleSx} color="primary">
              <StoreIcon /> Análisis de mercado
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
              {analisis.tamano_mercado != null ? <Chip size="small" label={`Mercado: ${String(analisis.tamano_mercado)}`} /> : null}
              {analisis.crecimiento_anual != null ? <Chip size="small" label={`Crecimiento: ${String(analisis.crecimiento_anual)}`} /> : null}
            </Box>
            {(analisis.competidores_principales ? renderList(analisis.competidores_principales) : null) as React.ReactNode}
            {analisis.ventaja_competitiva != null ? <Typography variant="body2" sx={{ mt: 1 }}>{String(analisis.ventaja_competitiva)}</Typography> : null}
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <Card sx={cardSx}>
          <CardContent>
            <Typography variant="h6" sx={sectionTitleSx} color="primary">Estrategia de precios</Typography>
            {precios.modelo != null ? <Typography variant="body2"><strong>Modelo:</strong> {String(precios.modelo)}</Typography> : null}
            {precios.justificacion != null ? <Typography variant="body2" sx={{ mt: 0.5 }}>{String(precios.justificacion)}</Typography> : null}
            {(precios.descuentos ? renderList(precios.descuentos) : null) as React.ReactNode}
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <Card sx={cardSx}>
          <CardContent>
            <Typography variant="h6" sx={sectionTitleSx} color="primary">Estrategia de marketing</Typography>
            {(marketing.canales_principales ? renderList(marketing.canales_principales) : null) as React.ReactNode}
            {marketing.presupuesto_mensual != null ? <Typography variant="body2" sx={{ mt: 1 }}>Presupuesto mensual: {String(marketing.presupuesto_mensual)}</Typography> : null}
            {(marketing.kpis ? renderList(marketing.kpis) : null) as React.ReactNode}
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <Card sx={cardSx}>
          <CardContent>
            <Typography variant="h6" sx={sectionTitleSx} color="primary">Estrategia de ventas</Typography>
            {ventas.proceso != null ? <Typography variant="body2"><strong>Proceso:</strong> {String(ventas.proceso)}</Typography> : null}
            {ventas.ciclo_venta_estimado != null ? <Typography variant="body2">Ciclo de venta: {String(ventas.ciclo_venta_estimado)}</Typography> : null}
            {ventas.tasa_conversion_objetivo != null ? <Typography variant="body2">Conversión objetivo: {String(ventas.tasa_conversion_objetivo)}</Typography> : null}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export const RoadmapCards: React.FC<{ data?: Record<string, unknown> }> = ({ data }) => {
  if (!data) return <Typography color="text.secondary">No hay datos de roadmap.</Typography>;
  const fases = (data.fases || []) as Array<Record<string, unknown>>;
  const totalMeses = data.cronograma_total_meses;
  return (
    <Box>
      {totalMeses != null && (
        <Chip label={`Cronograma total: ${totalMeses} meses`} color="primary" sx={{ mb: 2 }} />
      )}
      <Grid container spacing={2}>
        {fases.map((fase, i) => (
          <Grid size={{ xs: 12, md: 4 }} key={i}>
            <Card sx={{ ...cardSx, borderLeft: '4px solid', borderLeftColor: 'primary.main' }}>
              <CardContent>
                <Typography variant="h6" sx={sectionTitleSx}>
                  <TimelineIcon color="primary" /> {String(fase.fase ?? `Fase ${i + 1}`)}
                </Typography>
                {fase.duracion_meses != null ? <Chip size="small" label={`${fase.duracion_meses} meses`} sx={{ mb: 1 }} /> : null}
                {fase.hitos != null ? <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 1 }}>Hitos</Typography> : null}
                {(fase.hitos ? renderList(fase.hitos) : null) as React.ReactNode}
                {fase.recursos_necesarios ? (
                  <>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 1 }}>Recursos</Typography>
                    {renderList(fase.recursos_necesarios) as React.ReactNode}
                  </>
                ) : null}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export const AnalisisNumericosCards: React.FC<{ data?: Record<string, unknown> }> = ({ data }) => {
  if (!data) return <Typography color="text.secondary">No hay datos de análisis numérico.</Typography>;
  const inversion = (data.inversion_inicial || {}) as Record<string, unknown>;
  const proyecciones = (data.proyecciones_3_anos || []) as Array<Record<string, unknown>>;
  const metricas = (data.metricas_clave || {}) as Record<string, unknown>;
  const viabilidad = data.viabilidad_financiera;
  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Card sx={cardSx}>
          <CardContent>
            <Typography variant="h6" sx={sectionTitleSx} color="primary">
              <ChartIcon /> Inversión inicial
            </Typography>
            {inversion.total != null ? <Typography variant="h5" color="primary.main">{Number(inversion.total).toLocaleString()}</Typography> : null}
            {(inversion.desglose ? renderList(inversion.desglose as unknown[]) : null) as React.ReactNode}
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <Card sx={cardSx}>
          <CardContent>
            <Typography variant="h6" sx={sectionTitleSx} color="primary">Métricas clave</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              {metricas.roi_3_anos != null ? <Typography variant="body2"><strong>ROI 3 años:</strong> {String(metricas.roi_3_anos)}</Typography> : null}
              {metricas.punto_equilibrio_meses != null ? <Typography variant="body2"><strong>Punto equilibrio:</strong> {String(metricas.punto_equilibrio_meses)} meses</Typography> : null}
              {metricas.ltv_cac_ratio != null ? <Typography variant="body2"><strong>LTV/CAC:</strong> {String(metricas.ltv_cac_ratio)}</Typography> : null}
              {metricas.margen_bruto != null ? <Typography variant="body2"><strong>Margen bruto:</strong> {String(metricas.margen_bruto)}</Typography> : null}
            </Box>
            {viabilidad != null ? <Chip label={`Viabilidad: ${String(viabilidad)}`} color="success" size="small" sx={{ mt: 1 }} /> : null}
          </CardContent>
        </Card>
      </Grid>
      {proyecciones.length > 0 && (
        <Grid size={12}>
          <Card sx={cardSx}>
            <CardContent>
              <Typography variant="h6" sx={sectionTitleSx} color="primary">Proyecciones 3 años</Typography>
              <Grid container spacing={2}>
                {proyecciones.map((p, i) => {
                  const row = p as Record<string, unknown>;
                  return (
                    <Grid size={{ xs: 12, sm: 4 }} key={i}>
                      <Box sx={{ p: 1.5, bgcolor: 'action.hover', borderRadius: 2 }}>
                        <Typography variant="subtitle2">Año {String(row.ano ?? '')}</Typography>
                        <Typography variant="body2">Ingresos: {row.ingresos != null ? Number(row.ingresos).toLocaleString() : '-'}</Typography>
                        <Typography variant="body2">Costos: {row.costos != null ? Number(row.costos).toLocaleString() : '-'}</Typography>
                        <Typography variant="body2" fontWeight={600}>Utilidad: {row.utilidad_neta != null ? Number(row.utilidad_neta).toLocaleString() : '-'}</Typography>
                        {row.clientes_estimados != null ? (
                          <Typography variant="caption">Clientes: {String(row.clientes_estimados)}</Typography>
                        ) : null}
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
};

export const RiesgosCards: React.FC<{ data?: Record<string, unknown> }> = ({ data }) => {
  if (!data) return <Typography color="text.secondary">No hay datos de riesgos.</Typography>;
  const riesgos = (data.riesgos_identificados || []) as Array<Record<string, unknown>>;
  const nivel = data.nivel_riesgo_general;
  const recomendaciones = (data.recomendaciones || []) as unknown[];
  return (
    <Grid container spacing={2}>
      {nivel != null && nivel !== '' ? (
        <Grid size={12}>
          <Chip label={`Nivel de riesgo general: ${String(nivel)}`} color={nivel === 'ALTO' ? 'error' : nivel === 'MEDIO' ? 'warning' : 'success'} size="medium" />
        </Grid>
      ) : null}
      {riesgos.map((r, i) => (
        <Grid size={{ xs: 12, md: 6 }} key={i}>
          <Card sx={{ ...cardSx, borderLeft: '4px solid', borderLeftColor: (r.probabilidad === 'ALTA' || r.impacto === 'ALTO') ? 'error.main' : 'warning.main' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontSize: '1rem', mb: 0.5 }}>
                <WarningIcon sx={{ fontSize: 20, mr: 0.5 }} /> {String(r.riesgo)}
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 0.5 }}>
                {r.categoria != null ? <Chip size="small" label={String(r.categoria)} /> : null}
                {r.probabilidad != null ? <Chip size="small" variant="outlined" label={`Prob: ${String(r.probabilidad)}`} /> : null}
                {r.impacto != null ? <Chip size="small" variant="outlined" label={`Impacto: ${String(r.impacto)}`} /> : null}
              </Box>
              {r.mitigacion != null ? <Typography variant="body2" color="text.secondary">{String(r.mitigacion)}</Typography> : null}
            </CardContent>
          </Card>
        </Grid>
      ))}
      {recomendaciones.length > 0 && (
        <Grid size={12}>
          <Card sx={cardSx}>
            <CardContent>
              <Typography variant="h6" sx={sectionTitleSx} color="primary">Recomendaciones</Typography>
              {renderList(recomendaciones) as React.ReactNode}
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
};

export const VeredictoCards: React.FC<{ data?: Record<string, unknown> }> = ({ data }) => {
  if (!data) return <Typography color="text.secondary">No hay veredicto.</Typography>;
  const decision = data.decision;
  const puntuacion = data.puntuacion_general;
  const fortalezas = (data.fortalezas || []) as unknown[];
  const debilidades = (data.debilidades || []) as unknown[];
  const recomendacion = data.recomendacion_estrategica;
  const siguientePaso = data.siguiente_paso;
  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 4 }} key="decision">
        <Card sx={{ ...cardSx, bgcolor: decision === 'POSITIVO' ? 'success.50' : 'grey.100' }}>
          <CardContent>
            <Typography variant="h6" sx={sectionTitleSx} color="primary">
              <GavelIcon /> Decisión
            </Typography>
            <Chip label={String(decision || 'N/A')} color={decision === 'POSITIVO' ? 'success' : 'default'} size="medium" sx={{ mb: 1 }} />
            {puntuacion != null && <Typography variant="h4" color="primary.main">{Number(puntuacion)}/10</Typography>}
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <Card sx={cardSx}>
          <CardContent>
            <Typography variant="h6" sx={sectionTitleSx} color="primary">Fortalezas</Typography>
            {renderList(fortalezas) as React.ReactNode}
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <Card sx={cardSx}>
          <CardContent>
            <Typography variant="h6" sx={sectionTitleSx} color="primary">Debilidades</Typography>
            {renderList(debilidades) as React.ReactNode}
          </CardContent>
        </Card>
      </Grid>
      {(recomendacion != null && recomendacion !== '' ? (
        <Grid size={12} key="recomendacion">
          <Card sx={{ ...cardSx, borderLeft: '4px solid', borderLeftColor: 'primary.main' }}>
            <CardContent>
              <Typography variant="h6" sx={sectionTitleSx} color="primary">Recomendación estratégica</Typography>
              <Typography variant="body1">{String(recomendacion)}</Typography>
            </CardContent>
          </Card>
        </Grid>
      ) : null) as React.ReactNode}
      {(siguientePaso != null && siguientePaso !== '' ? (
        <Grid size={12} key="siguientePaso">
          <Card sx={cardSx}>
            <CardContent>
              <Typography variant="h6" sx={sectionTitleSx} color="primary">Siguiente paso</Typography>
              <Typography variant="body1">{String(siguientePaso)}</Typography>
            </CardContent>
          </Card>
        </Grid>
      ) : null) as React.ReactNode}
    </Grid>
  );
};
