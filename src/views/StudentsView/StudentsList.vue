<template>
  <ContainerView>
    <div class="page-wrap">
      <div class="content-panel">
        <div class="header">
          <h2 class="text-title">Alumnos</h2>
          <button class="btn primary" @click="router.push('/alumnos/nuevo')">
            Agregar alumno
          </button>
        </div>

        <div class="search-filter-section">
          <div class="filters">
            <div class="search-input-container">
              <i class="fas fa-search search-icon"></i>
              <input
                v-model="filters.nombre"
                class="search-input"
                placeholder="Buscar por nombre..."
              />
            </div>

            <select v-model="filters.estado" class="select">
              <option value="">Todos</option>
              <option value="activo">Activos</option>
              <option value="inactivo">Inactivos</option>
            </select>

            <select v-model="filters.residencia" class="select">
              <option value="">Residencia (todas)</option>
              <option value="Ciudad">Ciudad</option>
              <option value="Tello">Tello</option>
            </select>

            <button class="btn primary" @click="load()">Buscar</button>
            <button class="btn ghost" @click="reset()">Limpiar</button>
          </div>
        </div>

        <div class="permisos-table-container">
          <div class="table-wrapper">
            <table class="permisos-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Correo</th>
                  <th>Rol</th>
                  <th>Residencia</th>
                  <th>Hab.</th>
                  <th>Estado</th>
                  <th class="th-actions">Acciones</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="u in data.items" :key="u.id_usuario" class="table-row">
                  <td class="td-strong">{{ u.nombre }}</td>
                  <td>{{ u.correo }}</td>
                  <td>{{ u.rol }}</td>
                  <td>{{ u.residencia ?? '-' }}</td>
                  <td>{{ formatRoom(u) }}</td>
                  <td>
                    <span :class="['status-badge', u.estado === 'activo' ? 'status-approved' : 'status-pending']">
                      <i :class="u.estado === 'activo' ? 'fas fa-check' : 'fas fa-clock'"></i>
                      {{ u.estado ?? '-' }}
                    </span>
                  </td>
                  <td class="actions">
                    <button class="action-pill" @click="edit(u.id_usuario)">Editar</button>
                    <button class="action-pill ghost" @click="toggleEstado(u)">
                      {{ u.estado === 'activo' ? 'Inactivar' : 'Activar' }}
                    </button>
                  </td>
                </tr>

                <tr v-if="!loading && data.items.length === 0">
                  <td colspan="7" class="empty">Sin resultados</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="pagination-container">
          <div class="pagination-controls">
            <button class="pagination-btn" :disabled="data.page <= 1" @click="prev()">
              <i class="fas fa-chevron-left"></i>
            </button>
            <span class="pagination-text">Página {{ data.page }} de {{ data.pages }}</span>
            <button class="pagination-btn" :disabled="data.page >= data.pages" @click="next()">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>

      </div>
    </div>
  </ContainerView>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import ContainerView from '@/components/layout/ContainerView.vue'
import AdminUsuariosService from '@/services/AdminUsuariosService'
import type { User } from '@/models/User'

const router = useRouter()
const loading = ref(false)

const filters = reactive({
  nombre: '',
  estado: '',
  residencia: '',
  page: 1,
  per_page: 10,
})

const data = reactive({
  items: [] as User[],
  page: 1,
  per_page: 10,
  total: 0,
  pages: 1,
})

function formatRoom(u: User) {
  const p = u.pabellon ? `Pab ${u.pabellon}` : ''
  const h = u.habitacion ? `Hab ${u.habitacion}` : ''
  const t = [p, h].filter(Boolean).join(' - ')
  return t || '-'
}

async function load() {
  loading.value = true
  try {
    const res = await AdminUsuariosService.listar({
      nombre: filters.nombre || undefined,
      estado: filters.estado || undefined,
      residencia: filters.residencia || undefined,
      page: filters.page,
      per_page: filters.per_page,
    })
    Object.assign(data, res)
  } finally {
    loading.value = false
  }
}

function reset() {
  filters.nombre = ''
  filters.estado = ''
  filters.residencia = ''
  filters.page = 1
  load()
}

function edit(id: number) {
  router.push(`/alumnos/${id}/editar`)
}

async function toggleEstado(u: User) {
  const nuevo = u.estado === 'activo' ? 'inactivo' : 'activo'
  await AdminUsuariosService.cambiarEstado(u.id_usuario, nuevo as any)
  await load()
}

function prev() {
  if (filters.page > 1) {
    filters.page--
    load()
  }
}

function next() {
  if (filters.page < data.pages) {
    filters.page++
    load()
  }
}

onMounted(load)
</script>

<style scoped>
/* Layout: evita que se pegue a la derecha como te pasa en alumnos */
.page-wrap{
  width: 100%;
}

/* Panel estilo reportes (marronsito/oliva + borde dorado) */
.content-panel{
  background: rgba(154, 154, 122, 0.35);
  border: 1px solid #A37801;
  border-radius: 16px;
  padding: 24px;
  /* esto crea la separación a la derecha como reportes */
  margin: 24px 64px 24px 24px;
  backdrop-filter: blur(2px);
}

/* Header */
.header{
  display:flex;
  justify-content: space-between;
  align-items:center;
  gap: 12px;
  margin-bottom: 16px;
}

.text-title{
  color: white;
  font-size: 28px !important;
  text-transform: none;
  font-family: 'Righteous', cursive;
  margin: 0;
}

/* Botones */
.btn{
  border:none;
  border-radius: 14px;
  padding: 10px 14px;
  cursor:pointer;
  transition: all .2s ease;
  white-space: nowrap;
}

.btn.primary{
  background:#53696D;
  color: #fff;
}

.btn.ghost{
  background: #ffffffb8;
  border: 1px solid rgba(0,0,0,.12);
}

/* Search & Filters */
.search-filter-section{
  background: transparent;
  border-radius: 12px;
  border: 1px solid #A37801;
  padding: 16px;
  margin-bottom: 16px;
}

.filters{
  display:flex;
  gap:10px;
  flex-wrap: wrap;
  align-items: center;
}

.search-input-container{
  position: relative;
  flex: 1;
  min-width: 280px;
}

.search-icon{
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #111827;
  font-size: 16px;
}

.search-input{
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #A37801;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
}

.select{
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #A37801;
  min-width: 180px;
  background: #fff;
  font-size: 14px;
}

/* Tabla estilo reportes */
.permisos-table-container{
  background: transparent;
  border-radius: 12px;
  border: 1px solid #A37801;
  overflow: hidden;
  margin-bottom: 16px;
}

.table-wrapper{
  overflow-x: auto;
}

.permisos-table{
  width: 100%;
  border-collapse: collapse;
  min-width: 980px;
}

.permisos-table thead{
  background: #FFFBED;
}

.permisos-table th{
  padding: 16px 24px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #525252;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #A37801;
  white-space: nowrap;
}

.th-actions{
  text-align: right;
}

.permisos-table td{
  padding: 16px 24px;
  border-bottom: 1px solid #A37801;
  vertical-align: middle;
  font-size: 14px;
  color: #111827;
}

.td-strong{
  font-weight: 600;
}

.table-row:hover{
  background: #FFFBED;
}

.status-badge{
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid;
  gap: 8px;
  white-space: nowrap;
}

.status-approved{
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}

.status-pending{
  background: #fef3c7;
  color: #92400e;
  border-color: #fde68a;
}

.actions{
  display:flex;
  justify-content:flex-end;
  gap: 8px;
  white-space: nowrap;
}

.action-pill{
  border: none;
  border-radius: 999px;
  padding: 8px 12px;
  cursor: pointer;
  background: #eae6c9;
  font-size: 12px;
}

.action-pill.ghost{
  background: #ffffffb8;
  border: 1px solid rgba(0,0,0,.12);
}

.empty{
  text-align:center;
  padding:16px;
}

/* Paginación */
.pagination-container{
  display:flex;
  justify-content:center;
  padding: 12px 16px;
  background: transparent;
  border-radius: 12px;
  border: 1px solid #A37801;
}

.pagination-controls{
  display:flex;
  align-items:center;
  gap: 14px;
}

.pagination-btn{
  width: 32px;
  height: 32px;
  border: none;
  background: #FFFBED;
  color: #6b7280;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.pagination-btn:disabled{
  opacity: .5;
  cursor: not-allowed;
}

.pagination-text{
  font-size: 14px;
  color: #374151;
}

/* Responsive */
@media (max-width: 1024px){
  .content-panel{
    margin: 16px 16px 16px 16px; /* en pantallas medianas ya no dejes tanto margen */
  }
}

@media (max-width: 768px){
  .content-panel{
    padding: 16px;
    margin: 12px;
  }
  .text-title{ font-size: 22px !important; }
  .select{ min-width: 160px; }
  .search-input-container{ min-width: 220px; }
}
</style>