<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card class="pa-4 rounded-xl">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 class="text-h5 font-weight-bold text-pink">Agendar Cita</h2>
        <v-btn icon="fa-solid fa-xmark" variant="text" color="primary" @click="closeDialog" />
      </v-card-title>

      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <div class="mb-4" v-if="user.rol == UserRole.PSYCHOLOGIST || user.rol == UserRole.SOCIAL">
          <label class="text-body-2 font-weight-medium mb-2 d-block">Alumno</label>
          <v-autocomplete
            v-model="form.student"
            v-model:search="searchStudent"
            @update:search="searchDebouncedUsers"
            :items="students"
            item-title="nombre"
            item-value="id"
            :rules="[rules.requiredByRole]"
            variant="outlined"
            hide-details
            class="custom-input"
            placeholder="Buscar alumno por nombre..."
            return-object
            clearable
            :loading="loadingSearchStudent"
            density="compact"
          >
            <template v-slot:item="{ props, item }">
              <v-list-item
                v-bind="props"
                :title="item.raw.nombre"
                :subtitle="item.raw.correo"
              ></v-list-item>
            </template>
          </v-autocomplete>
        </div>
        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block">Motivo</label>
          <v-select
            v-model="form.reason_id"
            :items="reasonList"
            item-title="motivo"
            item-value="id"
            :rules="[rules.requiredByRole]"
            placeholder="Seleccione un motivo"
            variant="outlined"
            density="compact"
            class="custom-input"
            hide-details
            clearable
          />
        </div>

        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block">Especialista</label>
          <v-select
            v-model="form.specialist_id"
            :items="reasonList"
            item-title="area"
            item-value="id_area"
            :rules="[rules.requiredByRole]"
            variant="outlined"
            density="compact"
            class="custom-input"
            disabled
            hide-details
          />
        </div>

        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Descripción</label>
          <v-textarea
            v-model="form.description"
            placeholder="Ingrese una descripción (opcional)"
            variant="outlined"
            rows="4"
            density="compact"
            class="custom-input"
            hide-details
          />
        </div>

        <v-row class="mb-4" dense>
          <v-col cols="12" md="12">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Fecha</label>
            <VueDatePicker
              v-model="form.date"
              :rules="[rules.required]"
              locale="es"
              format="dd/MM/yyyy"
              :ui="{ input: 'custom-input' }"
              :enable-time-picker="false"
              placeholder="Selecciona la fecha"
              density="compact"
              hide-details
            />
          </v-col>
        </v-row>

        <v-row class="mb-4" dense>
          <v-col cols="12" md="6" sm="6">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Horario Inicio</label>
            <v-select
              v-model="form.startTime"
              :items="hoursList"
              :rules="[rules.required]"
              placeholder="Seleccionar hora inicio"
              variant="outlined"
              density="compact"
              class="custom-input"
              clearable
              @update:model-value="resetEndTime"
              hide-details
            />
          </v-col>

          <v-col cols="12" md="6" sm="6">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Horario Fin</label>
            <v-select
              v-model="form.endTime"
              :items="endHoursList"
              :rules="[rules.required]"
              placeholder="Seleccionar hora fin"
              variant="outlined"
              density="compact"
              class="custom-input"
              clearable
              hide-details
              :disabled="!form.startTime"
            />
          </v-col>
        </v-row>

        <div class="d-flex justify-center">
          <v-btn
            type="submit"
            color="#e91e63"
            size="large"
            style="border-radius: 20px; text-transform: none; font-weight: 500"
            min-width="120px"
          >
            Registrar
          </v-btn>
        </div>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { watch, computed } from 'vue'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { useCreateAppointmentModal } from './create-appointment-modal'
import './CreateAppointmentModal.scss'
import { UserRole } from '@/shared/enums/role.enum'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved'): void
}>()

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const {
  user,
  form,
  formRef,
  students,
  searchStudent,
  searchDebouncedUsers,
  loadingSearchStudent,
  reasonList,
  hoursList,
  endHoursList,
  rules,
  resetEndTime,
  handleSubmit,
  closeDialog,
} = useCreateAppointmentModal(emit)
</script>
