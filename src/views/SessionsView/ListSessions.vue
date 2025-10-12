<template>
  <ContainerView>
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
                <v-card-text class="pl-4">
                  <div class="mb-3">
                    <div>{{ appointment.descripcion }}</div>
                  </div>

                  <div class="d-flex flex-wrap align-center mb-3">
                    <span class="mr-2">Fecha de cita: </span>
                    <v-chip color="primary">{{ dateFormatV2(appointment.fecha) }}</v-chip>
                  </div>

                  <div class="d-flex flex-wrap align-center">
                    <span class="mr-2">Horario de cita:</span>
                    <v-chip color="secondary">{{ appointment.horario }}</v-chip>
                  </div>
                </v-card-text>
                <v-card-actions class="justify-center">
                  <v-chip variant="flat" :color="getStatusColor(appointment.estado)" size="large">
                    {{ appointment.estado }}
                  </v-chip>
                  <v-btn
                    v-if="
                      appointment.estado == AppointmentStatus.APROBADO ||
                      appointment.estado == AppointmentStatus.REPROGRAMADO
                    "
                    @click="openModalReschedule(appointment)"
                    icon
                    size="small"
                    variant="outlined"
                    class="action-btn view"
                    title="Reprogramar cita"
                  >
                    <v-icon size="18">mdi-calendar-arrow-right</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-tabs-window-item>

        <v-tabs-window-item value="busy-schedules">
          <v-row>
            <v-col cols="12" sm="6" md="5" lg="3">
              <v-autocomplete
                v-model="filtersBusySchedulesStudent.area_id"
                :items="listAreas"
                item-title="area"
                item-value="id_area"
                placeholder="Filtrar por Especialidad"
                variant="solo"
                density="compact"
                clearable
                class="filter-input"
              />
            </v-col>

            <v-col cols="12" sm="6" md="5" lg="3">
              <v-text-field
                v-model="filtersBusySchedulesStudent.date"
                type="date"
                variant="solo"
                density="compact"
                clearable
                class="filter-input"
              />
            </v-col>
          </v-row>

          <v-data-table
            :headers="columnsBusySchedulesStudent"
            :items="listBusySchedules"
            item-value="id"
            class="elevation-0 mt-4 rounded-lg data-table"
            density="comfortable"
            hide-default-footer
            disable-pagination
          >
            <template v-slot:item.fecha="{ item }">
              {{ dateFormatV2((item as any).fecha) }}
            </template>
          </v-data-table>
        </v-tabs-window-item>
      </v-tabs-window>
    </template>

    <!-- Vista para Admin, Psicologa o Trabajadora -->
    <template v-else>
      <div>
        <v-tabs v-model="adminTabActive" align-tabs="start" color="#A37801">
          <v-tab value="pending" class="custom-tab">
            <h4>Pendientes</h4>
          </v-tab>
          <v-tab value="completed" class="custom-tab">
            <h4>Culminadas</h4>
          </v-tab>
          <v-spacer></v-spacer>
          <v-btn variant="outlined" class="mb-6 custom-button" @click="openModalNewSession">
            <span>Solicitar una cita</span>
          </v-btn>
        </v-tabs>

        <v-tabs-window v-model="adminTabActive">
          <v-tabs-window-item value="pending">
            <div class="search-filter-section">
              <v-row align="center" dense class="mb-5">
                <v-col cols="12" md="9" lg="9">
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

                <!-- <v-col cols="12" md="6" lg="3">
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
                  </v-col> -->

                <v-col cols="12" md="3" lg="3">
                  <v-text-field
                    v-model="filters.fecha"
                    type="date"
                    variant="solo"
                    density="compact"
                    class="filter-input"
                    hide-details
                    clearable
                  />
                </v-col>

                <!-- <v-card class="pa-4">
                    <v-date-picker v-model="selectedDate" color="primary" />
                    <div class="mt-4">Fecha seleccionada: {{ selectedDate }}</div>
                  </v-card> -->
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

            <div v-if="smAndDown" class="mobile-reports-container mobile-only">
              <div
                v-for="appointment in appointmentsFiltered"
                :key="appointment.id"
                class="mobile-report-card"
              >
                <div class="mobile-card-header">
                  <div class="numero-badge">ID: {{ appointment.id }}</div>
                  <span class="status-badge">
                    <v-chip variant="flat" :color="getStatusColor(appointment.estado)">{{
                      appointment.estado
                    }}</v-chip>
                  </span>
                </div>

                <div class="mobile-card-content">
                  <h4 class="mobile-motivo">{{ appointment.motivo }}</h4>
                  <div class="mobile-info-row">
                    <div class="mobile-fecha">
                      <i class="fas fa-calendar"></i>
                      <span>{{ dateFormatV2(appointment.fecha) }}</span>
                    </div>
                    <div class="mobile-horario">
                      <i class="fas fa-tag"></i>
                      <span>{{ appointment.horario }}</span>
                    </div>
                  </div>
                  <p class="mobile-descripcion">
                    {{ appointment.descripcion?.substring(0, 80)
                    }}{{ appointment.descripcion?.length > 80 ? '...' : '' }}
                  </p>
                </div>

                <div class="mobile-card-actions">
                  <v-btn
                    @click="handleDetail(appointment.id)"
                    color="primary"
                    size="large"
                    variant="tonal"
                    class="mobile-action-btn"
                    prepend-icon="mdi-eye"
                  >
                    Ver detalles
                  </v-btn>

                  <v-btn
                    v-if="
                      appointment.estado == AppointmentStatus.SOLICITADO ||
                      appointment.estado == AppointmentStatus.APROBADO ||
                      !!appointment.reprog.solicitada_por
                    "
                    @click="openModalReschedule(appointment)"
                    color="secondary"
                    size="large"
                    variant="tonal"
                    class="mobile-action-btn"
                    prepend-icon="mdi-calendar-arrow-right"
                  >
                    Reprogramar cita
                  </v-btn>
                </div>
              </div>
            </div>

            <div v-else class="appointment-table-container">
              <div class="table-wrapper">
                <table class="appointment-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Nombre</th>
                      <!-- <th>Especialista</th> -->
                      <th>Motivo</th>
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
                            <!-- <div class="appointment-reason">{{ appointment.motivo || '' }}</div> -->
                          </div>
                        </div>
                      </td>
                      <td>
                        <!-- <div class="duration">{{ appointment.area }}</div> -->
                        <div class="duration">{{ appointment.motivo }}</div>
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
                            v-if="
                              appointment.estado == AppointmentStatus.SOLICITADO ||
                              appointment.estado == AppointmentStatus.APROBADO ||
                              !!appointment.reprog.solicitada_por
                            "
                            @click="openModalReschedule(appointment)"
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
                <span class="pagination-text"> Página {{ currentPage }} de {{ totalPages }} </span>
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
                <v-col cols="12" md="9" lg="9">
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

                <!-- <v-col cols="12" md="6" lg="3">
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
                  </v-col> -->

                <v-col cols="12" md="3" lg="3">
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

            <div v-if="smAndDown" class="mobile-reports-container mobile-only">
              <div
                v-for="appointment in appointmentsFiltered"
                :key="appointment.id"
                class="mobile-report-card"
              >
                <div class="mobile-card-header">
                  <div class="numero-badge">ID: {{ appointment.id }}</div>
                  <span class="status-badge">
                    <v-chip variant="flat" :color="getStatusColor(appointment.estado)">{{
                      appointment.estado
                    }}</v-chip>
                  </span>
                </div>

                <div class="mobile-card-content">
                  <h4 class="mobile-motivo">{{ appointment.motivo }}</h4>
                  <div class="mobile-info-row">
                    <div class="mobile-fecha">
                      <i class="fas fa-calendar"></i>
                      <span>{{ dateFormatV2(appointment.fecha) }}</span>
                    </div>
                    <div class="mobile-horario">
                      <i class="fas fa-tag"></i>
                      <span>{{ appointment.horario }}</span>
                    </div>
                  </div>
                  <p class="mobile-descripcion">
                    {{ appointment.descripcion?.substring(0, 80)
                    }}{{ appointment.descripcion?.length > 80 ? '...' : '' }}
                  </p>
                </div>

                <div class="mobile-card-actions">
                  <v-btn
                    @click="handleDetail(appointment.id)"
                    color="primary"
                    size="large"
                    variant="tonal"
                    class="mobile-action-btn"
                    prepend-icon="mdi-eye"
                  >
                    Ver detalles
                  </v-btn>
                </div>
              </div>
            </div>

            <div v-else class="appointment-table-container">
              <div class="table-wrapper">
                <table class="appointment-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Nombre</th>
                      <th>Motivo</th>
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
                            <!-- <div class="appointment-reason">{{ appointment.motivo || '' }}</div> -->
                          </div>
                        </div>
                      </td>
                      <td>
                        <!-- <div class="duration">{{ appointment.area }}</div> -->
                        <div class="duration">{{ appointment.motivo }}</div>
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
                <span class="pagination-text"> Página {{ currentPage }} de {{ totalPages }} </span>
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
      </div>
    </template>
  </ContainerView>

  <CreateAppointmentModal v-model="showModalNewSession" @saved="loadAppointments" />

  <DetailAppointmentModal
    v-model="showModalDetail"
    :appointment="selectedAppointment"
    :is-student="isStudent"
    @update-status="updateAppointmentStatus"
  />

  <RescheduleAppointmentModal
    v-model="showModalReschedule"
    :appointment="selectedAppointment"
    @saved="loadAppointments"
    @update-status="updateAppointmentStatus"
  />
</template>

<script setup lang="ts">
import './list-sessions.scss'
import { AppointmentStatus } from '@/shared/enums/appointment-status.enum'
import { dateFormatV2 } from '@/shared/util/functions'
import { useSessionList } from './list-sessions'
import ContainerView from '@/components/layout/ContainerView.vue'
import CreateAppointmentModal from '../modal/Citas/CreateAppointmentModal/CreateAppointmentModal.vue'
import RescheduleAppointmentModal from '../modal/Citas/RescheduleAppointmentModal/RescheduleAppointmentModal.vue'
import DetailAppointmentModal from '../modal/Citas/DetailAppointmentModal/DetailAppointmentModal.vue'

import { ref } from 'vue'
import { useDisplay } from 'vuetify'

const { smAndDown } = useDisplay()

const selectedDate = ref<string | null>(null)

const {
  isStudent,
  listAreas,
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
  handleDetail,
  showModalDetail,
  selectedAppointment,
  openModalNewSession,
  showModalNewSession,
  openModalReschedule,
  showModalReschedule,
  updateAppointmentStatus,
  getStatusColor,
} = useSessionList()
</script>
