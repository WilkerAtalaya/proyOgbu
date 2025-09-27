<template>
  <ContainerModal
    v-model="dialog"
    :title="`Detalle de Cita #${appointment?.id || 'N/A'}`"
    :max-width="650"
    :colorTheme="'#A37801'"
  >
    <v-card-text>
      <v-list density="compact">
        <v-list-item>
          <v-list-item-title class="font-weight-bold text-subtitle-1">Alumno </v-list-item-title>
          <v-list-item-subtitle class="mt-2 mb-4">{{
            appointment?.nombre || '-'
          }}</v-list-item-subtitle>
        </v-list-item>

        <v-list-item>
          <v-list-item-title class="font-weight-bold text-subtitle-1"
            >Especialista
          </v-list-item-title>
          <v-list-item-subtitle class="mt-2 mb-4 text-body-2">{{
            appointment?.area || '-'
          }}</v-list-item-subtitle>
        </v-list-item>

        <v-list-item>
          <v-list-item-title class="font-weight-bold text-subtitle-1">Motivo</v-list-item-title>
          <v-list-item-subtitle class="mt-2 mb-4 text-body-2">{{
            appointment?.motivo || '-'
          }}</v-list-item-subtitle>
        </v-list-item>

        <v-list-item>
          <v-list-item-title class="font-weight-bold text-subtitle-1"
            >Descripción</v-list-item-title
          >
          <v-list-item-subtitle class="mt-2 mb-4 text-body-2">{{
            appointment?.descripcion || '-'
          }}</v-list-item-subtitle>
        </v-list-item>

        <v-list-item>
          <v-list-item-title class="font-weight-bold text-subtitle-1">Fecha</v-list-item-title>
          <v-list-item-subtitle class="mt-2 mb-4 text-body-2">{{
            appointment ? dateFormatV2(appointment.fecha) : '-'
          }}</v-list-item-subtitle>
        </v-list-item>

        <v-list-item>
          <v-list-item-title class="font-weight-bold text-subtitle-1">Horario</v-list-item-title>
          <v-list-item-subtitle class="mt-2 mb-4 text-body-2">{{
            appointment?.horario || '-'
          }}</v-list-item-subtitle>
        </v-list-item>
      </v-list>
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
          >Cancelar</v-btn
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
