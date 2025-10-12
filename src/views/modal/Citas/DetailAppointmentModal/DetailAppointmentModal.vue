<template>
  <ContainerModal
    v-model="dialog"
    :title="`Detalle de Cita #${appointment?.id || 'N/A'}`"
    :max-width="650"
    :colorTheme="'#A37801'"
  >
    <v-card-text>
      <v-row
        v-for="(item, i) in [
          { label: 'Alumno:', value: appointment?.nombre || '-' },
          { label: 'Especialista:', value: appointment?.area || '-' },
          { label: 'Motivo:', value: appointment?.motivo || '-' },
          { label: 'Descripción:', value: appointment?.descripcion || '-' },
          { label: 'Fecha:', value: appointment?.fecha ? dateFormatV2(appointment.fecha) : '-' },
          { label: 'Horario:', value: appointment?.horario || '-' },
        ]"
        :key="i"
      >
        <v-col cols="12" sm="4" md="4" lg="3" class="font-weight-bold text-subtitle-1">
          {{ item.label }}
        </v-col>
        <v-col cols="12" sm="8" md="8" lg="9" class="text-body-2">
          {{ item.value }}
        </v-col>
      </v-row>

      <template v-if="appointment?.reprog?.solicitada_por !== null">
        <hr class="my-4"></hr>
        <v-row class="py-1">
          <v-col cols="12" sm="4" md="4" lg="5" class="font-weight-bold text-subtitle-1">
            Nueva fecha solicitada:
          </v-col>
          <v-col cols="12" sm="8" md="8" lg="7" class="text-body-2">
            {{ appointment?.reprog?.fecha ? dateFormatV2(appointment?.reprog.fecha): '-' }}
          </v-col>
        </v-row>
        <v-row class="py-1">
          <v-col cols="12" sm="4" md="4" lg="5" class="font-weight-bold text-subtitle-1">
            Nuevo horario solicitado:
          </v-col>
          <v-col cols="12" sm="8" md="8" lg="7" class="text-body-2">
            {{ appointment?.reprog?.horario ?? '-' }}
          </v-col>
        </v-row>
      </template>
    </v-card-text>

    <v-card-actions class="my-2 d-flex justify-end" v-if="!isStudent">
      <template v-if="appointment?.estado == AppointmentStatus.SOLICITADO">
        <v-btn
          color="success"
          rounded="xl"
          size="large"
          min-width="130"
          elevation="2"
          variant="flat"
          @click="handleUpdateStatus(AppointmentStatus.APROBADO)"
          >Aprobar</v-btn
        >
        <!-- <v-btn
          color="error"
          rounded="xl"
          size="large"
          min-width="130"
          elevation="2"
          variant="flat"
          @click="handleUpdateStatus(AppointmentStatus.RECHAZADO)"
          >Rechazar</v-btn
        > -->
        <v-btn
          color="grey"
          rounded="xl"
          size="large"
          min-width="130"
          elevation="2"
          variant="flat"
          @click="dialog = false"
          >Cerrar</v-btn
        >
      </template>

      <template v-if="appointment?.estado == AppointmentStatus.APROBADO">
        <v-btn
          color="teal"
          rounded="xl"
          size="large"
          min-width="130"
          elevation="2"
          variant="flat"
          @click="handleUpdateStatus(AppointmentStatus.ATENDIDO)"
          >Atendido
        </v-btn>
        <v-btn
          color="grey"
          rounded="xl"
          size="large"
          min-width="130"
          elevation="2"
          variant="flat"
          @click="handleUpdateStatus(AppointmentStatus.AUSENTE)"
          >Ausente
        </v-btn>
      </template>
    </v-card-actions>
  </ContainerModal>
</template>

<script setup lang="ts">
import './DetailAppointmentModal.scss'
import { watch, computed } from 'vue'
import { dateFormatV2 } from '@/shared/util/functions'
import ContainerModal from '@/components/layout/ContainerModal.vue'
import { AppointmentStatus } from '@/shared/enums/appointment-status.enum'
import type { Cita } from '@/models/Cita'

const props = defineProps<{
  modelValue: boolean
  appointment: Cita | null
  isStudent: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'update-status', status: string): void
}>()

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const handleUpdateStatus = (status: string) => {
  emit('update-status', status)
  dialog.value = false
}
</script>
