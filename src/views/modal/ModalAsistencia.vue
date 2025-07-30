<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card class="pa-4" style="border-radius: 16px">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 class="text-h5 font-weight-bold" style="color: #e91e63">Reporte Detallado de Asistencia</h2>
        <button
          @click="dialog = false"
          style="background: none; border: none; cursor: pointer"
          title="Cerrar Modal"
        >
          <i class="fa-solid fa-xmark" style="color: #1976d2; font-size: 20px"></i>
        </button>
      </v-card-title>

      <div class="mb-4">
        <label class="text-body-2 font-weight-medium mb-2 d-block">Información de Asistencia</label>
        <div v-for="(item, index) in asistencias" :key="index" class="mb-3">
          <v-card 
            class="pa-3" 
            style="border-radius: 8px; background-color: #f8f9fa; border-left: 4px solid #e91e63"
          >
            <div class="d-flex flex-column">
              <div class="mb-2">
                <span class="text-body-2 font-weight-medium">Fecha:</span>
                <span class="ml-2">{{ dateFormatV2(item.fecha) }}</span>
              </div>
              <div class="mb-2">
                <span class="text-body-2 font-weight-medium">Hora marcada:</span>
                <span class="ml-2">{{ dateFormatV3(item.hora_marcado) }}</span>
              </div>
              <div>
                <span class="text-body-2 font-weight-medium">Alumno:</span>
                <span class="ml-2">{{ item.nombre_alumno }}</span>
              </div>
            </div>
          </v-card>
        </div>
      </div>

      <div class="d-flex justify-center">
        <v-btn
          @click="dialog = false"
          color="#1976d2"
          size="large"
          style="border-radius: 20px; text-transform: none; font-weight: 500"
          min-width="120px"
        >
          Cerrar
        </v-btn>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, watch } from 'vue'
import { dateFormatV2, dateFormatV3 } from '@/util/functions.js'

const props = defineProps({
  modelValue: Boolean,
  asistencias: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

watch(
  () => props.asistencias,
  (val) => {
    if (val) {
      console.log('Asistencias recibidas en ModalAsistencia:', val)
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.custom-input :deep(.v-field) {
  border-radius: 8px;
  background-color: #f8f9fa;
}

.custom-input :deep(.v-field--focused) {
  background-color: white;
}
</style>
