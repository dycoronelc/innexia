import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  DragIndicator as DragIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Flag as FlagIcon,
  Event as EventIcon
} from '@mui/icons-material';
import ActivityCard from './ActivityCard';
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  rectIntersection,
  useDroppable
} from '@dnd-kit/core';
import type {
  DragEndEvent,
  DragStartEvent,
  CollisionDetection,
  UniqueIdentifier
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy
} from '@dnd-kit/sortable';
import {
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { ProjectActivity } from '../types';

interface ProjectKanbanProps {
  activities: ProjectActivity[];
  onUpdateActivities: (activities: ProjectActivity[]) => void;
  projectId: string;
  availableTags: Array<{ id: string; name: string; color: string }>;
  availableUsers: Array<{ id: string; fullName: string; username: string; role: string }>;
  availableCategories: Array<{ id: string; name: string; color: string }>;
}

interface KanbanColumn {
  id: string;
  title: string;
  color: string;
  activities: ProjectActivity[];
}

interface DraggableCardProps {
  activity: ProjectActivity;
  onEdit: (activity: ProjectActivity) => void;
  onDelete: (activityId: string) => void;
  onStatusChange: (activityId: string, newStatus: ProjectActivity['status']) => void;
  columnId: string;
  availableTags: Array<{ id: string; name: string; color: string }>;
  availableUsers: Array<{ id: string; fullName: string; username: string; role: string }>;
  availableCategories: Array<{ id: string; name: string; color: string }>;
}

interface DroppableColumnProps {
  column: KanbanColumn;
  onEdit: (activity: ProjectActivity) => void;
  onDelete: (activityId: string) => void;
  onStatusChange: (activityId: string, newStatus: ProjectActivity['status']) => void;
  availableTags: Array<{ id: string; name: string; color: string }>;
  availableUsers: Array<{ id: string; fullName: string; username: string; role: string }>;
  availableCategories: Array<{ id: string; name: string; color: string }>;
}

// Componente de tarjeta arrastrable
const DraggableCard: React.FC<DraggableCardProps> = ({ 
  activity, 
  onEdit, 
  onDelete, 
  onStatusChange, 
  columnId,
  availableTags,
  availableUsers,
  availableCategories
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: activity.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  // Preparar la actividad para el nuevo ActivityCard
  const enhancedActivity = {
    ...activity,
    assignees: activity.assignee ? [activity.assignee] : [],
    tags: [],
    comments: [],
    checklists: [],
    attachments: [],
    labels: []
  };

  return (
    <Box
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
    >
      <ActivityCard
        activity={enhancedActivity}
        onUpdate={(updatedActivity) => {
          // Convertir de vuelta al formato esperado
          const convertedActivity = {
            ...updatedActivity,
            assignee: updatedActivity.assignees[0] || ''
          };
          onEdit(convertedActivity);
        }}
        onDelete={onDelete}
        availableTags={availableTags}
        availableUsers={availableUsers}
        availableCategories={availableCategories}
      />
    </Box>
  );
};

// Componente de columna droppable
const DroppableColumn: React.FC<DroppableColumnProps> = ({ 
  column, 
  onEdit, 
  onDelete, 
  onStatusChange,
  availableTags,
  availableUsers,
  availableCategories
}) => {
  const { setNodeRef } = useDroppable({
    id: column.id,
  });

  return (
    <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(25% - 6px)' }, minWidth: { md: 'calc(25% - 6px)' } }}>
      <Paper
        sx={{
          p: 2,
          height: '100%',
          backgroundColor: 'background.paper',
          borderTop: `4px solid ${column.color}`,
          minHeight: 400
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ color: column.color, fontWeight: 'bold' }}>
            {column.title}
          </Typography>
          <Chip 
            label={column.activities.length} 
            size="small" 
            sx={{ backgroundColor: column.color, color: 'white' }}
          />
        </Box>

        <Box
          ref={setNodeRef}
          sx={{
            minHeight: 300,
            backgroundColor: 'action.hover',
            borderRadius: 1,
            p: 1,
            border: '2px dashed',
            borderColor: 'divider',
            borderStyle: 'dashed'
          }}
        >
          <SortableContext
            items={column.activities.map(activity => activity.id)}
            strategy={verticalListSortingStrategy}
          >
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {column.activities.map((activity) => (
                <DraggableCard
                  key={activity.id}
                  activity={activity}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  onStatusChange={onStatusChange}
                  columnId={column.id}
                  availableTags={availableTags}
                  availableUsers={availableUsers}
                  availableCategories={availableCategories}
                />
              ))}
            </Box>
          </SortableContext>
        </Box>
      </Paper>
    </Box>
  );
};

const ProjectKanban: React.FC<ProjectKanbanProps> = ({
  activities,
  onUpdateActivities,
  projectId,
  availableTags,
  availableUsers,
  availableCategories
}) => {
  const [columns, setColumns] = useState<KanbanColumn[]>([
    {
      id: 'todo',
      title: 'Por Hacer',
      color: '#1976d2',
      activities: activities.filter(a => a.status === 'todo')
    },
    {
      id: 'in-progress',
      title: 'En Progreso',
      color: '#ed6c02',
      activities: activities.filter(a => a.status === 'in-progress')
    },
    {
      id: 'review',
      title: 'En Revisión',
      color: '#9c27b0',
      activities: activities.filter(a => a.status === 'review')
    },
    {
      id: 'completed',
      title: 'Completado',
      color: '#2e7d32',
      activities: activities.filter(a => a.status === 'completed')
    }
  ]);

  const [openDialog, setOpenDialog] = useState(false);
  const [editingActivity, setEditingActivity] = useState<ProjectActivity | null>(null);
  const [activeId, setActiveId] = useState<UniqueIdentifier | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'todo' as ProjectActivity['status'],
    priority: 'medium' as ProjectActivity['priority'],
    assignee: '',
    startDate: '',
    dueDate: ''
  });

  // Mock data for form options - Usuarios con rol "Usuario"
  const users = [
    { id: '1', username: 'juan.perez', fullName: 'Juan Pérez', role: 'user' },
    { id: '2', username: 'maria.garcia', fullName: 'María García', role: 'user' },
    { id: '3', username: 'carlos.rodriguez', fullName: 'Carlos Rodríguez', role: 'user' },
    { id: '4', username: 'ana.martinez', fullName: 'Ana Martínez', role: 'user' },
    { id: '5', username: 'luis.hernandez', fullName: 'Luis Hernández', role: 'user' }
  ];

  // Configurar sensores para drag and drop
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  // Update columns when activities change
  useEffect(() => {
    setColumns(prevColumns => 
      prevColumns.map(col => ({
        ...col,
        activities: activities.filter(a => a.status === col.id)
      }))
    );
  }, [activities]);

  const handleAddActivity = () => {
    setEditingActivity(null);
    setFormData({
      title: '',
      description: '',
      status: 'todo',
      priority: 'medium',
      assignee: '',
      startDate: '',
      dueDate: ''
    });
    setOpenDialog(true);
  };

  const handleEditActivity = (activity: ProjectActivity) => {
    setEditingActivity(activity);
    setFormData({
      title: activity.title,
      description: activity.description,
      status: activity.status,
      priority: activity.priority,
      assignee: activity.assignee,
      startDate: activity.startDate.toISOString().split('T')[0],
      dueDate: activity.dueDate.toISOString().split('T')[0]
    });
    setOpenDialog(true);
  };

  const handleDeleteActivity = (activityId: string) => {
    const updatedActivities = activities.filter(a => a.id !== activityId);
    onUpdateActivities(updatedActivities);
  };

  const handleSaveActivity = () => {
    if (!formData.title.trim()) return;

    const newActivity: ProjectActivity = {
      id: editingActivity?.id || Date.now().toString(),
      title: formData.title.trim(),
      description: formData.description.trim(),
      status: formData.status,
      priority: formData.priority,
      assignee: formData.assignee.trim(),
      assignees: editingActivity?.assignees ?? [],
      startDate: new Date(formData.startDate),
      dueDate: new Date(formData.dueDate),
      createdAt: editingActivity?.createdAt || new Date(),
      updatedAt: new Date(),
      projectId: Number(projectId),
      tags: editingActivity?.tags ?? [],
      comments: editingActivity?.comments ?? [],
      checklists: editingActivity?.checklists ?? [],
      attachments: editingActivity?.attachments ?? [],
      labels: editingActivity?.labels ?? []
    };

    let updatedActivities: ProjectActivity[];
    if (editingActivity) {
      updatedActivities = activities.map(a => 
        a.id === editingActivity.id ? newActivity : a
      );
    } else {
      updatedActivities = [...activities, newActivity];
    }

    onUpdateActivities(updatedActivities);
    setOpenDialog(false);
  };

  const handleStatusChange = (activityId: string, newStatus: ProjectActivity['status']) => {
    const updatedActivities = activities.map(a => 
      a.id === activityId ? { ...a, status: newStatus, updatedAt: new Date() } : a
    );
    onUpdateActivities(updatedActivities);
  };

  // Función para detectar colisiones mejorada
  const collisionDetection: CollisionDetection = (args) => {
    return rectIntersection(args);
  };

  // Manejar el inicio del drag
  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id);
  };



  // Manejar el fin del drag
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    
    if (!over) {
      setActiveId(null);
      return;
    }

    const activeId = active.id;
    const overId = over.id;

    if (activeId === overId) {
      setActiveId(null);
      return;
    }

    // Encontrar las columnas de origen y destino
    const activeColumn = columns.find(col => 
      col.activities.some(activity => activity.id === activeId)
    );
    const overColumn = columns.find(col => col.id === overId);

    if (!activeColumn || !overColumn) {
      setActiveId(null);
      return;
    }

    // Si se arrastra a una columna diferente, actualizar el estado
    if (activeColumn.id !== overColumn.id) {
      const updatedActivities = activities.map(activity => 
        activity.id === activeId 
          ? { ...activity, status: overColumn.id as ProjectActivity['status'], updatedAt: new Date() }
          : activity
      );
      onUpdateActivities(updatedActivities);
    }

    setActiveId(null);
  };

  // Obtener la actividad activa para el overlay
  const activeActivity = activeId 
    ? activities.find(activity => activity.id === activeId)
    : null;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Tablero Kanban - Actividades del Proyecto
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddActivity}
        >
          Nueva Actividad
        </Button>
      </Box>

      {/* Kanban Board con Drag and Drop */}
      <DndContext
        sensors={sensors}
        collisionDetection={collisionDetection}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
                 {/* ===== KANBAN BOARD - LAYOUT OPTIMIZADO AL 100% ===== */}
                 <Box sx={{ display: 'flex', gap: 2, minHeight: 600, width: '100%' }}>
                   {columns.map((column) => (
                     <DroppableColumn
                       key={column.id}
                       column={column}
                       onEdit={handleEditActivity}
                       onDelete={handleDeleteActivity}
                       onStatusChange={handleStatusChange}
                       availableTags={availableTags}
                       availableUsers={availableUsers}
                       availableCategories={availableCategories}
                     />
                   ))}
                 </Box>

        {/* Drag Overlay */}
        <DragOverlay>
          {activeActivity ? (
            <Card
              sx={{
                cursor: 'grabbing',
                boxShadow: 8,
                border: '2px solid',
                borderColor: 'primary.main',
                transform: 'rotate(5deg)',
                maxWidth: 300
              }}
            >
              <CardContent sx={{ p: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                  {activeActivity.title}
                </Typography>
                {activeActivity.description && (
                  <Typography variant="body2" color="text.secondary">
                    {activeActivity.description}
                  </Typography>
                )}
              </CardContent>
            </Card>
          ) : null}
        </DragOverlay>
      </DndContext>


    </Box>
  );
};

export default ProjectKanban;
