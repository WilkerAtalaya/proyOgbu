<template>
  <ContainerView background-color="transparent" padding="0px">
    <div class="citas-container">
      <!-- <div class="citas-header">
          <table cellspacing="0" cellpadding="8"style="border-collapse: collapse; width: auto; text-align: left; margin: 0; font-family: sans-serif;">
            <thead>
              <tr style="background-color: #f9f9f9;">
                <th style="border: 1px solid #ccc; padding: 12px;">Mes</th>
                <th style="border: 1px solid #ccc; padding: 12px;">Hora de atención</th>
              </tr>
            </thead>
            <tbody>
              <tr style="background-color: #e0e0e0;">
                <td style="border: 1px solid #ccc; padding: 12px;">Mayo</td>
                <td style="border: 1px solid #ccc; padding: 12px;">
                  <div>09:00am - 12:00pm</div>
                  <div>02:00pm - 05:00pm</div>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="text-right">
            <v-btn variant="outlined" class="mb-6" @click="openModalNewSession()">Agendar Cita</v-btn>
          </div>
        </div> -->

      <!-- Vista para Estudiantes -->
      <template v-if="isStudent">
        <v-tabs v-model="studentTabActive" class="mb-4" align-tabs="start" color="#A37801">
          <v-tab value="appointment-list" class="custom-tab">
            <h3 :class="{ 'active-tab-text': studentTabActive === 'appointment-list' }">Citas</h3>
          </v-tab>
          <v-tab value="busy-schedules" class="custom-tab">
            <h3 :class="{ 'active-tab-text': studentTabActive === 'busy-schedules' }">
              Horarios Ocupados
            </h3>
          </v-tab>
          <v-spacer></v-spacer>
          <v-btn variant="outlined" class="mb-6 custom-button" @click="openModalNewSession">
            <span>Solicitar una cita</span>
          </v-btn>
        </v-tabs>

        <v-tabs-window v-model="studentTabActive">
          <v-tabs-window-item value="appointment-list">
            <v-row>
              <v-col
                v-for="appointment in appointmentsFiltered"
                :key="appointment.id"
                cols="12"
                sm="6"
                md="4"
                lg="3"
              >
                <v-card class="pa-2" rounded="xl">
                  <v-card-title>{{ appointment.area }}</v-card-title>
                  <v-card-subtitle>{{ appointment.motivo }}</v-card-subtitle>
                  <v-card-text class="ma-2 pa-2">
                    <v-row>
                      <v-col cols="12">
                        <div>{{ appointment.descripcion }}</div>
                      </v-col>
                    </v-row>

                    <v-row>
                      <v-col cols="12" sm="12" md="12" lg="5">
                        <v-chip color="primary">{{ dateFormatV2(appointment.fecha) }}</v-chip>
                      </v-col>
                      <v-col cols="12" sm="12" md="12" lg="7">
                        <v-chip color="secondary">{{ appointment.horario }}</v-chip>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  <v-card-actions class="justify-center">
                    <v-chip variant="flat" :color="getStatusColor(appointment.estado)" size="large">{{
                      appointment.estado
                    }}</v-chip>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
            <!-- <n-data-table
              class="data-table"
              ref="dataTableInst"
              :columns="columnsAlumno"
              :data="dataAlumno"
              :pagination="pagination"
              /> -->
            <!-- <n-modal v-model:show="showModal" preset="dialog" class="modal-cita">
              <template #header>
                <h2 style="color: #a1003c; text-align: center">Agendar Cita</h2>
              </template>
              <div class="form-cita">
                <div>
                  <label>Motivo:</label>
                  <n-input placeholder="Motivo de la cita" v-model:value="form.motivo" />
                </div>
                <div>
                  <label>Descripción:</label>
                  <n-input
                    type="textarea"
                    placeholder="Describe el motivo..."
                    v-model:value="form.descripcion"
                  />
                </div>
                <div>
                  <label>Área disponible:</label>
                  <n-select
                    v-model:value="form.area"
                    :options="[
                      { label: 'Psicología', value: 'psicologia' },
                      { label: 'Bienestar', value: 'bienestar' },
                    ]"
                  />
                </div>
                <div class="horario-seleccionado">
                  <label>Horario elegido:</label>
                  <div class="slot-box">
                    <strong>{{ selectedSlot?.day }}</strong>
                    <span>{{ selectedSlot?.hour }}</span>
                  </div>
                </div>
                <div style="text-align: center; margin-top: 16px">
                  <n-button type="primary" style="background-color: #a1003c" @click="submitCita"
                    >Enviar</n-button
                  >
                </div>
              </div>
            </n-modal> -->
          </v-tabs-window-item>

          <v-tabs-window-item value="busy-schedules">
            <v-row>
              <v-col cols="12" sm="6" md="4" lg="3">
                <v-autocomplete
                  v-model="filtersBusySchedulesStudent.area_id"
                  :items="listAreas"
                  item-title="area"
                  item-value="id_area"
                  placeholder="Filtrar por Área"
                  variant="solo"
                  density="compact"
                  clearable
                />
              </v-col>

              <v-col cols="12" sm="6" md="4" lg="3">
                <v-autocomplete
                  v-model="filtersBusySchedulesStudent.date"
                  :items="['fecha 1', 'fecha 2']"
                  item-title="name"
                  item-value="id"
                  placeholder="Filtrar por Fecha"
                  variant="solo"
                  density="compact"
                  clearable
                />
              </v-col>
            </v-row>
            <!-- <n-data-table
              class="data-table"
              ref="dataTableInst"
              :columns="columnsBusySchedulesStudent"
              :data="listBusySchedules"
              :pagination="pagination"
            /> -->
            <v-data-table
              :headers="columnsBusySchedulesStudent"
              :items="listBusySchedules"
              item-value="id"
              class="elevation-0 mt-4 rounded-lg data-table"
              density="comfortable"
              hide-default-footer
              disable-pagination
            />
          </v-tabs-window-item>
        </v-tabs-window>
      </template>

      <!-- Vista para Admin -->
      <template v-else>
        <div>
          <v-tabs v-model="adminTabActive" align-tabs="start" color="#A37801">
            <v-tab value="pending" class="custom-tab">
              <h4>Pendientes</h4>
            </v-tab>
            <v-tab value="completed" class="custom-tab">
              <h4>Culminadas</h4>
            </v-tab>
          </v-tabs>

          <!-- <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px">
            <n-input
              v-model:value="filters.area"
              placeholder="Área"
              style="flex: 1; min-width: 150px"
            />
            <n-input
              v-model:value="filters.nombre"
              placeholder="Nombre"
              style="flex: 1; min-width: 150px"
            />
            <n-input
              v-model:value="filters.id_numero"
              placeholder="ID número"
              style="flex: 1; min-width: 150px"
            />
            <n-date-picker
              v-model:value="filters.fecha"
              type="date"
              placeholder="Fecha"
              format="dd/MM/yyyy"
              value-format="yyyy-MM-dd"
            />
            <n-button @click="loadAppointments" type="primary" style="min-width: 100px"
              >Buscar</n-button
            >
            <n-button @click="clearFilters" secondary style="min-width: 100px">Limpiar</n-button>
          </div> -->

          <v-tabs-window v-model="adminTabActive">
            <v-tabs-window-item value="pending">
              <div class="search-filter-section">
                <v-row align="center" dense class="mb-5">
                  <v-col cols="12" md="12" lg="6">
                    <div class="search-input-container">
                      <i class="fas fa-search search-icon"></i>
                      <input
                        type="text"
                        placeholder="Buscar por nombre o motivo..."
                        class="search-input"
                        v-model="filters.search"
                        clearable
                      />
                    </div>
                  </v-col>

                  <v-col cols="12" md="6" lg="3">
                    <v-select
                      v-model="filters.area_id"
                      :items="listAreas"
                      item-title="area"
                      item-value="id_area"
                      placeholder="Filtrar por especialista"
                      variant="solo"
                      density="compact"
                      hide-details
                      clearable
                    />
                  </v-col>

                  <v-col cols="12" md="6" lg="3">
                    <n-date-picker
                      v-model:value="filters.fecha"
                      type="date"
                      placeholder="Fecha"
                      format="dd/MM/yyyy"
                      value-format="yyyy-MM-dd"
                      class="w-full"
                      clearable
                    />
                  </v-col>
                </v-row>

                <div class="filter-tabs">
                  <button
                    v-for="tab in statusFilterByTab"
                    :key="tab.value"
                    @click="filters.status = tab.value"
                    :class="['filter-tab', { active: filters.status === tab.value }]"
                  >
                    {{ tab.label }}
                  </button>
                </div>
              </div>

              <!-- <div class="search-filter-section">
                <v-row class="align-center">
                  <v-col cols="12" sm="4" md="4" lg="4">
                    <v-text-field
                      v-model="filters.search"
                      density="compact"
                      variant="outlined"
                      hide-details
                      placeholder="Buscar por nombre o motivo..."
                      prepend-inner-icon="fas fa-search"
                      class="search-input"
                      clearable
                    />
                  </v-col>

                  <v-col cols="12" sm="4" md="4" lg="4">
                    <v-select
                      v-model="filters.area"
                      :items="listAreas"
                      item-title="area"
                      item-value="id_area"
                      label="Filtrar por especialista"
                      variant="outlined"
                      density="compact"
                      hide-details
                      clearable
                    />
                  </v-col>

                  <v-col cols="12" sm="4" md="4" lg="4">
                    <n-date-picker
                      v-model:value="filters.fecha"
                      type="date"
                      placeholder="Fecha"
                      format="dd/MM/yyyy"
                      value-format="yyyy-MM-dd"
                      class="w-full"
                    />
                  </v-col>
                </v-row>

                <v-row>
                  <div class="filter-tabs">
                    <button
                      v-for="tab in statusFilter"
                      :key="tab.value"
                      @click="filters.status = tab.value"
                      :class="['filter-tab', { active: filters.status === tab.value }]"
                    >
                      {{ tab.label }}
                    </button>
                  </div>
                </v-row>
              </div> -->

              <div class="appointment-table-container">
                <div class="table-wrapper">
                  <table class="appointment-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Especialista</th>
                        <th>Fecha</th>
                        <th>Horario</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="appointment in appointmentsFiltered"
                        :key="appointment.id"
                        class="table-row"
                      >
                        <td>
                          <div class="appointment-id">{{ appointment.id }}</div>
                        </td>
                        <td>
                          <div class="appointment-info">
                            <div class="appointment-details">
                              <div class="appointment-bold">{{ appointment.nombre || '' }}</div>
                              <div class="appointment-reason">{{ appointment.motivo || '' }}</div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div class="duration">{{ appointment.area }}</div>
                        </td>
                        <td>
                          <div class="appointment-bold">{{ dateFormatV2(appointment.fecha) }}</div>
                        </td>
                        <td>
                          <div class="appointment-bold">{{ appointment.horario }}</div>
                        </td>
                        <td>
                          <v-chip variant="flat" :color="getStatusColor(appointment.estado)">{{
                            appointment.estado
                          }}</v-chip>
                        </td>
                        <td>
                          <div class="d-flex justify-center ga-1">
                            <!-- <button v-if="permiso.archivo_justificacion" @click="downloadFile(permiso.archivo_justificacion)" 
                              class="action-btn download" title="Descargar archivo">
                              <i class="fas fa-download"></i>
                            </button>-->
                            <v-btn
                              @click="handleDetail(appointment.id)"
                              icon
                              size="small"
                              variant="outlined"
                              class="action-btn view"
                              title="Ver detalles"
                            >
                              <v-icon size="18">mdi-eye</v-icon>
                            </v-btn>
                            <v-btn
                              v-if="appointment.estado == AppointmentStatus.APROBADO"
                              @click="openModalReschedule(appointment.id)"
                              icon
                              size="small"
                              variant="outlined"
                              class="action-btn view"
                              title="Reprogramar cita"
                            >
                              <v-icon size="18">mdi-calendar-arrow-right</v-icon>
                            </v-btn>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div class="pagination-container">
                <div class="pagination-info">
                  <span>Mostrar</span>
                  <select v-model="itemsPerPage" class="items-select">
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="25">25</option>
                    <option value="50">50</option>
                  </select>
                  <span>de {{ appointmentsFilteredTotal.length }} resultados</span>
                </div>
                <div class="pagination-controls">
                  <button
                    @click="currentPage = Math.max(currentPage - 1, 1)"
                    :disabled="currentPage === 1"
                    class="pagination-btn"
                  >
                    <i class="fas fa-chevron-left"></i>
                  </button>
                  <span class="pagination-text">
                    Página {{ currentPage }} de {{ totalPages }}
                  </span>
                  <button
                    @click="currentPage = Math.min(currentPage + 1, totalPages)"
                    :disabled="currentPage === totalPages"
                    class="pagination-btn"
                  >
                    <i class="fas fa-chevron-right"></i>
                  </button>
                </div>
              </div>
            </v-tabs-window-item>

            <v-tabs-window-item value="completed">
              <div class="search-filter-section">
                <v-row align="center" dense class="mb-5">
                  <v-col cols="12" md="12" lg="6">
                    <div class="search-input-container">
                      <i class="fas fa-search search-icon"></i>
                      <input
                        type="text"
                        placeholder="Buscar por nombre o motivo..."
                        class="search-input"
                        v-model="filters.search"
                        clearable
                      />
                    </div>
                  </v-col>

                  <v-col cols="12" md="6" lg="3">
                    <v-select
                      v-model="filters.area_id"
                      :items="listAreas"
                      item-title="area"
                      item-value="id_area"
                      placeholder="Filtrar por especialista"
                      variant="solo"
                      density="compact"
                      hide-details
                      clearable
                    />
                  </v-col>

                  <v-col cols="12" md="6" lg="3">
                    <n-date-picker
                      v-model:value="filters.fecha"
                      type="date"
                      placeholder="Fecha"
                      format="dd/MM/yyyy"
                      value-format="yyyy-MM-dd"
                      class="w-full"
                      clearable
                    />
                  </v-col>
                </v-row>

                <div class="filter-tabs">
                  <button
                    v-for="tab in statusFilterByTab"
                    :key="tab.value"
                    @click="filters.status = tab.value"
                    :class="['filter-tab', { active: filters.status === tab.value }]"
                  >
                    {{ tab.label }}
                  </button>
                </div>
              </div>

              <div class="appointment-table-container">
                <div class="table-wrapper">
                  <table class="appointment-table">
                    <thead>
                      <tr>
                        <th>Nombre</th>
                        <th>Especialista</th>
                        <th>Fecha</th>
                        <th>Horario</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="appointment in appointmentsFiltered"
                        :key="appointment.id"
                        class="table-row"
                      >
                        <td>
                          <div class="appointment-info">
                            <div class="appointment-details">
                              <div class="appointment-bold">{{ appointment.nombre || '' }}</div>
                              <div class="appointment-id">{{ appointment.motivo || '' }}</div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div class="duration">{{ appointment.area }}</div>
                        </td>
                        <td>
                          <div class="appointment-bold">{{ dateFormatV2(appointment.fecha) }}</div>
                        </td>
                        <td>
                          <div class="appointment-bold">{{ appointment.horario }}</div>
                        </td>
                        <td>
                          <v-chip variant="flat" :color="getStatusColor(appointment.estado)">{{
                            appointment.estado
                          }}</v-chip>
                        </td>
                        <td>
                          <div class="actions">
                            <!-- <button v-if="permiso.archivo_justificacion" @click="downloadFile(permiso.archivo_justificacion)" 
                              class="action-btn download" title="Descargar archivo">
                              <i class="fas fa-download"></i>
                            </button>
                            <button @click="viewDetails(permiso)" class="action-btn view" title="Ver detalles">
                              <i class="fas fa-eye"></i>
                            </button> -->
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div class="pagination-container">
                <div class="pagination-info">
                  <span>Mostrar</span>
                  <select v-model="itemsPerPage" class="items-select">
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="25">25</option>
                    <option value="50">50</option>
                  </select>
                  <span>de {{ appointmentsFilteredTotal.length }} resultados</span>
                </div>
                <div class="pagination-controls">
                  <button
                    @click="currentPage = Math.max(currentPage - 1, 1)"
                    :disabled="currentPage === 1"
                    class="pagination-btn"
                  >
                    <i class="fas fa-chevron-left"></i>
                  </button>
                  <span class="pagination-text">
                    Página {{ currentPage }} de {{ totalPages }}
                  </span>
                  <button
                    @click="currentPage = Math.min(currentPage + 1, totalPages)"
                    :disabled="currentPage === totalPages"
                    class="pagination-btn"
                  >
                    <i class="fas fa-chevron-right"></i>
                  </button>
                </div>
              </div>
            </v-tabs-window-item>
          </v-tabs-window>

          <!-- <n-tabs v-model:value="adminTabActive" type="line">
            <n-tab-pane name="pendientes" tab="Pendientes">
              <n-data-table
                ref="tablaPendientes"
                :columns="columnsAdmin"
                :data="dataPendiente"
                :pagination="pagination"
              />
            </n-tab-pane>
            <n-tab-pane name="culminadas" tab="Culminadas">
              <n-data-table
                ref="tablaCulminadas"
                :columns="columnsAdmin"
                :data="dataCulminada"
                :pagination="pagination"
              />
            </n-tab-pane>
          </n-tabs> -->
        </div>
      </template>
    </div>
  </ContainerView>

  <CreateAppointmentModal v-model="showModalNewSession" @saved="loadAppointments" />

  <DetailAppointmentModal
    v-model="showModalDetail"
    :appointment="appointmentToView"
    :is-student="isStudent"
    @update-status="updateAppointmentStatus"
  />

  <RescheduleAppointmentModal
    v-model="showModalReschedule"
    :appointment-id="selectedAppointmentId"
  />

</template>

<script setup lang="ts">
import './list-sessions.scss'
import { useSessionList } from './list-sessions'
import CreateAppointmentModal from '../modal/Citas/CreateAppointmentModal/CreateAppointmentModal.vue'
import RescheduleAppointmentModal from '../modal/Citas/RescheduleAppointmentModal/RescheduleAppointmentModal.vue'
import DetailAppointmentModal from '../modal/Citas/DetailAppointmentModal/DetailAppointmentModal.vue'
import ContainerView from '@/components/layout/ContainerView.vue'
import { AppointmentStatus } from '@/shared/enums/appointment-status.enum'

const {
  isAdmin,
  isStudent,
  user,
  listAreas,
  listReasons,
  studentTabActive,
  columnsBusySchedulesStudent,
  filtersBusySchedulesStudent,
  listBusySchedules,
  adminTabActive,
  loadAppointments,
  appointmentsFiltered,
  appointmentsFilteredTotal,
  currentPage,
  itemsPerPage,
  totalPages,
  pagination,
  filters,
  statusFilterByTab,
  clearFilters,
  form,
  submitCita,
  showModal,
  selectedSlot,
  dateFormatV2,
  dataTableInst,
  handleDetail,
  showModalDetail,
  appointmentToView,
  selectedAppointmentId,
  showModalNewSession,
  openModalNewSession,
  showModalReschedule,
  openModalReschedule,
  getStatusColor,
  updateAppointmentStatus,
  snackbar,
} = useSessionList()
</script>
