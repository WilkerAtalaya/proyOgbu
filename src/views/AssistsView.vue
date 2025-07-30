<template>
  <div class="pa-4">
    <v-card
      class="pa-6"
      style="
        border-radius: 16px;
        background-color: #BBBDA7;
        border: 3px solid #4a90e2;
      "
      elevation="4"
    >
      <h3 class="mb-4 text-title">Reporte de Asistencia</h3>

      <v-row class="mb-6">
        <v-col cols="12" sm="6">
          <v-select
            v-model="selectedYear"
            :items="years"
            label="Año"
            variant="outlined"
            density="comfortable"
            class="custom-select"
            @update:model-value="updateAttendanceData"
          ></v-select>
        </v-col>
        <v-col cols="12" sm="6">
          <v-select
            v-model="selectedMonth"
            :items="months"
            item-title="name"
            item-value="value"
            label="Mes"
            variant="outlined"
            density="comfortable"
            class="custom-select"
            @update:model-value="updateAttendanceData"
          ></v-select>
        </v-col>
      </v-row>

      <n-data-table
        class="data-table"
        :columns="columns"
        :data="asistenciasMarcadas"
        :pagination="pagination"
      />
    </v-card>

    <ModalAsistencia 
      v-model="reportDialog" 
      :asistencias="selectedRecord" 
    />

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false"> Cerrar </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted, h, resolveComponent } from 'vue'
import { NDataTable, NButton } from 'naive-ui'
import AsistenciaService from '@/services/AsistenciaService'
import LoginService from '@/services/LoginService'
import { dateFormatV1, dateFormatV2, dateFormatV3 } from '@/util/functions.js'
import ModalAsistencia from './modal/ModalAsistencia.vue'

const selectedYear = ref('2024')
const selectedMonth = ref('marzo')
const reportDialog = ref(false)
const selectedRecord = ref([])
const asistenciasMarcadas = ref([])
const user = ref(LoginService.getCurrentUser())
const snackbar = reactive({ show: false, message: '', color: 'success' })
const years = ['2022', '2023', '2024', '2025']
const months = [
  { name: 'Enero', value: 'enero' },
  { name: 'Febrero', value: 'febrero' },
  { name: 'Marzo', value: 'marzo' },
  { name: 'Abril', value: 'abril' },
  { name: 'Mayo', value: 'mayo' },
  { name: 'Junio', value: 'junio' },
  { name: 'Julio', value: 'julio' },
  { name: 'Agosto', value: 'agosto' },
  { name: 'Septiembre', value: 'septiembre' },
  { name: 'Octubre', value: 'octubre' },
  { name: 'Noviembre', value: 'noviembre' },
  { name: 'Diciembre', value: 'diciembre' },
]

const columns = [
  { 
    title: 'Fecha', 
    key: 'fecha',
    render(row) {
      return dateFormatV2(row.fecha)
    }
  },
  {
    title: 'Asistencia',
    key: 'asistencia',
    width: 150,
    render(row) {
      const NButton = resolveComponent('n-button')
      return h(
        NButton,
        {
          type: 'warning',
          size: 'small',
          onClick: () => handleStatusClick(row)
        },
        { default: () => 'Ver detalles' }
      )
    }
  }
]

const pagination = ref({ pageSize: 7 })

onMounted(async () => {
  await Promise.all[loadAsistenciasMarcadasPorUsuario()]
})

async function handleStatusClick(record) {
    const asistencias = await AsistenciaService.obtenerAsistenciaPorFechaYUsuario(record.usuario, record.fecha)
    selectedRecord.value = asistencias.map((a) => ({
      fecha: a.fecha,
      hora_marcado: a.hora_marcado,
      id: a.id,
      id_usuario: a.id_usuario,
      nombre_alumno: a.nombre_alumno,
    }))
    reportDialog.value = true
}

const updateAttendanceData = () => {
  snackbar.message = `Datos actualizados para ${selectedMonth.value} ${selectedYear.value}`
  snackbar.color = 'info'
  snackbar.show = true
  console.log('Actualizando datos para:', selectedYear.value, selectedMonth.value)
}

async function loadAsistenciasMarcadasPorUsuario() {
  const asistencias = await AsistenciaService.obtenerFechasMarcadasPorUsuario(user.value.id)
  asistencias.forEach((asistencia) => {
    asistenciasMarcadas.value.push({
      fecha: asistencia,
      usuario: user.value.id
    })
  })
}


</script>

<style scoped>
.custom-select :deep(.v-field) {
  border-radius: 8px;
  background-color: #f5f5f5;
}

.custom-select :deep(.v-field--focused) {
  background-color: white;
}

.custom-select :deep(.v-field__input) {
  color: #424242;
  font-weight: 500;
}

.text-title{
  color: rgb(163, 120, 1);
  font-size: 28px !important;
  font-size: larger;
  text-transform: none;
  font-family: 'Righteous', cursive;
}

::v-deep(.n-data-table-table) {
  border-radius: 20px !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: white;
}
::v-deep(.n-data-table) {
  border-radius: 20px !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: white;
}

::v-deep(.n-data-table-th) {
  background-color: #D9D9D9;
  color: black;
  font-weight: bold !important;
}

::v-deep(.n-data-table-td) {
  background-color: transparent !important;
  padding: 8px;
}

::v-deep(.n-data-table-th__title){
  color: #163053 !important;
}
</style>
