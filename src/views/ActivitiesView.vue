<template>
  <v-card class="contenido">
    <v-tabs v-model="tab" align-tabs="start" color="#A37801">
      <v-tab :value="1" class="custom-tab">Actividades</v-tab>
      <v-tab :value="2" class="custom-tab">Mis Solicitudes</v-tab>
    </v-tabs>
    <v-tabs-window v-model="tab">
      <v-tabs-window-item :value="1">
        <div  class="text-right">
          <v-btn variant="outlined" class="mb-6" @click="openModalNuevo">
            <span v-if="isAdmin"> Nueva Actividad </span>
            <span v-else>Solicitar Actividad</span>
          </v-btn>
        </div>
        <v-container fluid>
          <div v-for="(actividad, index) in actividades" :key="index" class="actividad-card">
            <div class="info">
              <div class="titulo-actividad">
                📌 <strong>{{ actividad.titulo }}</strong>
                <div class="fecha">({{ actividad.fecha }})</div>
              </div>
              <div class="descripcion">
                <small>Descripción</small><br />
                {{ actividad.descripcion || 'Sin descripción' }}
              </div>
            </div>
            <div class="tipo">{{ actividad.tipo.toUpperCase() }}</div>
            <div class="accion">
              <n-button  style="background-color:#ffc107;" type="warning"  @click="openModalNuevo('form')">Acceder al formulario</n-button>
            </div>
          </div>
        </v-container>
      </v-tabs-window-item>
      <v-tabs-window-item :value="2">
        <v-container fluid>
          <div class="pa-4">
            <v-card class="elevation-2" style="border-radius: 12px">
              <v-data-table
                :headers="headers"
                :items="items"
                class="custom-table"
                hide-default-footer
                :items-per-page="-1"
              >
                <template v-slot:item.codigo="{ item }">
                  <span class="text-body-2 font-weight-medium text-grey-darken-1">
                    {{ item.codigo }}
                  </span>
                </template>
                <template v-slot:item.titulo="{ item }">
                  <span class="text-body-2 font-weight-medium">
                    {{ item.titulo }}
                  </span>
                </template>
                <template v-slot:item.fecha="{ item }">
                  <span class="text-body-2 text-grey-darken-1">
                    {{ item.fecha }}
                  </span>
                </template>
                <template v-slot:item.resumen="{ item }">
                  <span class="text-body-2 text-grey-darken-1">
                    {{ item.descripcion }}
                  </span>
                </template>
                <template v-slot:item.acciones="{ item }">
                  <v-menu>
                    <template v-slot:activator="{ props }">
                      <button
                        v-bind="props"
                        style="background: none; border: none; cursor: pointer"
                        title="Ver detalle"
                         @click="openModalSolicitudes(item)"
                      >
                        <i
                          class="fa-solid fa-eye"
                          style="color: #1976d2; font-size: 20px"
                        ></i>
                      </button>
                    </template>
                    
                  </v-menu>
                </template>
              </v-data-table>
            </v-card>
            <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
              {{ snackbar.message }}
              <template v-slot:actions>
                <v-btn variant="text" @click="snackbar.show = false"> Cerrar </v-btn>
              </template>
            </v-snackbar>
          </div>
        </v-container>
      </v-tabs-window-item>
    </v-tabs-window>
  </v-card>
  <ModalActividades :type="modalType" v-model="showModal" :item="selectedItem" :user="user" :mode="isView" @agregar-actividad="agregarActividad" />
   <ModalMisSolicitudes v-model="showModalSolicitudes" :item="selectedItem" :user="user" :mode="isView" />
</template>
<script setup>
import { NButton } from 'naive-ui'
import { ref, reactive, onMounted } from 'vue'
import LoginService from '@/services/LoginService'
import ActividadesService from '@/services/ActividadesService'
import ModalActividades from './modal/ModalActividades.vue'
import ModalMisSolicitudes from './modal/ModalMisSolicitudes.vue'

const tab = ref(1)
const items = ref([])
const actividades = ref([])
const showModal = ref(false)
const modalType = ref('actividad')
const showModalSolicitudes = ref(false)
const selectedItem = ref(null)
const user = ref(LoginService.getCurrentUser())
const isAdmin = LoginService.isAdmin()
const snackbar = reactive({
  show: false,
  message: '',
  color: 'success',
})
const headers = [
  {
    title: 'Código',
    align: 'start',
    sortable: true,
    key: 'codigo',
    width: '100px',
  },
  {
    title: 'Título',
    align: 'start',
    sortable: true,
    key: 'titulo',
    width: '250px',
  },
  {
    title: 'Fecha',
    align: 'start',
    sortable: true,
    key: 'fecha',
    width: '150px',
  },
  {
    title: 'Resumen',
    align: 'start',
    sortable: false,
    key: 'resumen',
  },
  {
    title: 'Acciones',
    align: 'center',
    sortable: false,
    key: 'acciones',
    width: '100px',
  },
]

onMounted(async () => {
  await Promise.all[loadActividadesAprobadas(), chooseSolicitudes()]
})

const editItem = (item) => {
  snackbar.message = `Editando elemento: ${item.titulo}`
  snackbar.color = 'info'
  snackbar.show = true
}

const viewItem = (item) => {
  snackbar.message = `Viendo detalles de: ${item.titulo}`
  snackbar.color = 'info'
  snackbar.show = true
}

const deleteItem = (item) => {
  if (confirm(`¿Estás seguro de que quieres eliminar "${item.titulo}"?`)) {
    const index = items.value.findIndex((i) => i.id === item.id)
    if (index > -1) {
      items.value.splice(index, 1)
      snackbar.message = `Elemento eliminado: ${item.titulo}`
      snackbar.color = 'success'
      snackbar.show = true
    }
  }
}

function agregarActividad(actividad) {
  actividades.value.unshift(actividad)
}


function openModalNuevo( type = 'actividad') {
  const user = LoginService.getCurrentUser()
  selectedItem.value = {
    numero: '',
    asunto: '',
    motivo: '',
    fecha: '',
    estado: '',
    descripcion: '',
    attend : false
  }
  modalType.value = type
  showModal.value = true
}

function openModalSolicitudes(item) {
  selectedItem.value = item
  showModalSolicitudes.value = true
}

function chooseSolicitudes() {
  if (LoginService.isAdmin()) {
    loadSolicitudes()
  } else {
    loadSolicitudesPorUsuario()
  }
}

async function loadSolicitudesPorUsuario() {
  try {
    const activities = await ActividadesService.obtenerActividadesPorUsuario(user.value.id)
    items.value = activities.map((a) => ({
      id: a.id,
      codigo: `UNMSM-${a.id}`,
      titulo: a.titulo,
      fecha: a.fecha_actividad,
      resumen: a.descripcion,
      descripcion: a.descripcion,
      tipo: a.tipo,
    }))
  } catch (error) {
    console.error(error)
  }
}

async function loadSolicitudes() {
  try {
    const activities = await ActividadesService.obtenerTodas()
    items.value = activities.map((a) => ({
      id: a.id,
      codigo: `UNMSM-${a.id}`,
      titulo: a.titulo,
      fecha: a.fecha_actividad,
      resumen: a.descripcion,
      descripcion: a.descripcion,
      tipo: a.tipo,
    }))
  } catch (error) {
    console.error(error)
  }
}

async function loadActividadesAprobadas() {
  try {
    const activities = await ActividadesService.obtenerActividadesAprobadas()
    actividades.value = activities.map((a) => ({
      codigo: `UNMSM-${a.id}`,
      fecha: a.fecha_actividad,
      descripcion: a.descripcion,
      titulo: a.titulo,
      tipo: a.tipo.toUpperCase(),
    }))
  } catch (error) {
    console.error(error)
  }
}
</script>

<style scoped>
.custom-tab {
  font-size: larger;
  color: #f5f5f5;
  font-size: 20px;
  font-weight: 700;
  font-family: 'Righteous', cursive;
}

.actividades-wrapper {
  display: flex;
  gap: 20px;
  padding: 30px;
  background: url('/ruta/a/tu/fondo.png') no-repeat center;
  background-size: cover;
  min-height: 100vh;
  position: relative;
}

.perfil {
  position: absolute;
  top: 20px;
  left: 20px;
  background: #1e1e1e;
  color: white;
  padding: 8px 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.estado {
  width: 10px;
  height: 10px;
  background: limegreen;
  border-radius: 50%;
}

.sidebar {
  width: 220px;
  margin-top: 100px;
}

.contenido {
  flex: 1;
  background: rgba(197, 199, 176, 0.95);
  padding: 20px;
  border-radius: 20px;
  margin-left: auto;
}

.titulo {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.titulo .resaltado {
  color: #b28700;
  margin-right: 10px;
}

.actividad-card {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 12px;
  padding: 15px 20px;
  margin-bottom: 16px;
  justify-content: space-between;
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
}

.info {
  flex: 1;
}

.titulo-actividad {
  color: #163053;
  font-size: 16px;
  font-weight: bold;
}

.fecha {
  font-size: 13px;
  color: #555;
}

.descripcion {
  font-size: 14px;
  margin-top: 5px;
}

.tipo {
  font-size: 12px;
  text-align: center;
  color: #555;
  width: 100px;
}

.accion {
  min-width: 160px;
  display: flex;
  justify-content: flex-end;
}

/*Mis actividades*/
.custom-table :deep(.v-data-table__wrapper) {
  border-radius: 12px;
}

.custom-table :deep(.v-data-table-header) {
  background-color: #f5f5f5;
}

.custom-table :deep(.v-data-table-header__content) {
  font-weight: 600;
  color: #424242;
}

.custom-table :deep(.v-data-table__td) {
  padding: 16px 12px;
  border-bottom: 1px solid #e0e0e0;
}

.custom-table :deep(.v-data-table__th) {
  padding: 16px 12px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #616161;
}

.custom-table :deep(tbody tr:hover) {
  background-color: #f8f9fa;
}

.custom-table :deep(tbody tr:last-child td) {
  border-bottom: none;
}
</style>
