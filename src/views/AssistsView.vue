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
      <h2 class="text-h4 font-weight-bold mb-6" style="color: #b8860b">Reporte de Asistencia</h2>

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

      <v-card class="pa-0" style="border-radius: 12px; background-color: #f5f5f5" elevation="2">
        <v-row class="ma-0 pa-4" style="background-color: #e0e0e0; border-radius: 12px 12px 0 0">
          <v-col cols="6" class="pa-2">
            <h4 class="text-h6 font-weight-bold text-grey-darken-2">Fecha</h4>
          </v-col>
          <v-col cols="6" class="pa-2 text-center">
            <h4 class="text-h6 font-weight-bold text-grey-darken-2">Asistencia</h4>
          </v-col>
        </v-row>

        <div v-for="(record, index) in asistenciasMarcadas" :key="index">
          <v-row
            class="ma-0 pa-4 align-center"
            :class="{ 'bg-grey-lighten-4': index % 2 === 0 }"
            style="border-bottom: 1px solid #e0e0e0"
          >
            <v-col cols="6" class="pa-2">
              <span class="text-body-1 font-weight-medium text-grey-darken-2">
                {{ dateFormatV2(record.fecha) }}
              </span>
            </v-col>
            <v-col cols="6" class="pa-2 text-center">
              <v-btn
                color="warning"
                size="small"
                style="border-radius: 16px; text-transform: none; font-weight: 500"
                min-width="100px"
                @click="handleStatusClick(record)"
              >
                {{ 'Ver detalles' }}
              </v-btn>
            </v-col>
          </v-row>
        </div>
      </v-card>
    </v-card>

    <v-dialog v-model="reportDialog" max-width="500px">
      <v-card class="pa-4">
        <v-card-title class="text-h5 font-weight-bold"> Reporte Detallado </v-card-title>
        <v-card-text v-for="(item, index) in selectedRecord" :key="index">
          <p><strong>Fecha:</strong> {{ dateFormatV2(item.fecha) }}</p>
          <p><strong>Hora marcada:</strong> {{ dateFormatV3(item.hora_marcado) }}</p>
          <p><strong>Alumno:</strong> {{ item.nombre_alumno }}</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="close()"> Cerrar </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false"> Cerrar </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import AsistenciaService from '@/services/AsistenciaService'
import LoginService from '@/services/LoginService'
import { dateFormatV1, dateFormatV2, dateFormatV3 } from '@/util/functions.js'

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

const close = () => {
  reportDialog.value = false
  selectedRecord.value = []
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
</style>
