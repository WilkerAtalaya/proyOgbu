<template>
  <!-- Vista para estudiantes -->
  <ContainerView v-if="!isAdmin" background-color="transparent" padding="0px">
    <div class="student-permissions-container">
      <div class="form-column">
        <div class="form-card">
          <v-tabs v-model="activeTab" class="mb-4">
            <v-tab value="solicitud" class="custom-tab">
              <h3 :class="{ 'active-tab-text': activeTab === 'solicitud' }">
                Salida de vivienda
              </h3>
            </v-tab>
            <v-tab value="area-comun" class="custom-tab">
              <h3 :class="{ 'active-tab-text': activeTab === 'area-comun' }">Uso de área común</h3>
            </v-tab>
          </v-tabs>

          <v-tabs-window v-model="activeTab">
            <v-tabs-window-item value="solicitud">
              <div class="form-content">
                <div class="form-header">
                  <h2 class="form-title">Nueva solicitud de salida</h2>
                  <p class="form-subtitle">Registre el rango de días que estaras fuera de la vivienda universitaria:</p>
                </div>

                <v-form @submit.prevent="submitSolicitudVivienda" class="form-spacing">
                  <div class="form-group">
                    <label class="form-label">Periodo de ausencia</label>
                    <div class="date-range-container">
                      <div class="date-field">
                        <label class="date-sublabel">Fecha de salida</label>
                        <VueDatePicker 
                          v-model="form.fechaSalida" 
                          locale="es" 
                          format="dd/MM/yyyy"
                          :enable-time-picker="false" 
                          :min-date="new Date()" 
                          placeholder="Selecciona fecha de salida"
                          class="custom-input" 
                        />
                      </div>
                      <div class="date-field">
                        <label class="date-sublabel">Fecha de regreso</label>
                        <VueDatePicker 
                          v-model="form.fechaRegreso" 
                          locale="es" 
                          format="dd/MM/yyyy"
                          :enable-time-picker="false" 
                          :min-date="form.fechaSalida || new Date()" 
                          placeholder="Selecciona fecha de regreso"
                          class="custom-input" 
                        />
                      </div>
                    </div>
                    <div v-if="form.fechaSalida && form.fechaRegreso" class="duration-info">
                      <i class="fas fa-clock duration-icon"></i>
                      Duración: {{ calculateDays(form.fechaSalida, form.fechaRegreso) }} días
                    </div>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Motivo de la salida</label>
                    <v-textarea 
                      v-model="form.motivo" 
                      variant="outlined" 
                      rows="4" 
                      hide-details
                      placeholder="Describe brevemente el motivo de tu salida..."
                      class="custom-input"
                    ></v-textarea>
                    <p class="helper-text">Mínimo 10 caracteres</p>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Archivo de justificación</label>
                    <div class="upload-area" @click="triggerFileInputSalida">
                      <i class="fas fa-file-upload upload-icon"></i>
                      <span class="upload-text">
                        {{ selectedFileSalida ? selectedFileSalida.name : 'Haz clic para seleccionar un archivo' }}
                      </span>
                      <p class="upload-helper">PDF, JPG o PNG (máx. 5MB)</p>
                      <input 
                        ref="fileInputSalida" 
                        type="file" 
                        accept=".pdf,.jpg,.jpeg,.png" 
                        style="display: none" 
                        @change="handleFileSelectSalida" 
                      />
                    </div>
                  </div>

                  <div class="form-submit">
                    <v-btn 
                      type="submit" 
                      class="submit-btn primary-btn"
                      :loading="isSubmittingSalida"
                      :disabled="isSubmittingSalida"
                    >
                      <i v-if="!isSubmittingSalida" class="fas fa-paper-plane"></i>
                      {{ isSubmittingSalida ? 'Enviando...' : 'Enviar solicitud' }}
                    </v-btn>
                  </div>
                </v-form>
              </div>
            </v-tabs-window-item>

            <v-tabs-window-item value="area-comun">
              <div class="form-content">
                <div class="form-header">
                  <h2 class="form-title">Reserva de área común</h2>
                  <p class="form-subtitle">Registre el lugar, fecha y horario que quieres reservar</p>
                </div>

                <v-form @submit.prevent="submitAreaComun" class="form-spacing">
                  <div class="form-group">
                    <label class="form-label">Lugar</label>
                    <v-select 
                      v-model="form.lugar" 
                      :items="siteOptions" 
                      variant="outlined" 
                      density="comfortable"
                      hide-details 
                      class="custom-input"
                    ></v-select>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Motivo de la reserva</label>
                    <v-textarea 
                      v-model="form.motivoAreaComun" 
                      variant="outlined" 
                      rows="4" 
                      hide-details
                      placeholder="Describe brevemente el motivo de tu reserva..."
                      class="custom-input"
                    ></v-textarea>
                    <p class="helper-text">Mínimo 10 caracteres</p>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Fecha</label>
                    <VueDatePicker 
                      v-model="form.fechaAreaComun" 
                      locale="es" 
                      format="dd/MM/yyyy"
                      :enable-time-picker="false" 
                      :min-date="new Date()" 
                      placeholder="Selecciona la fecha"
                      class="custom-input" 
                    />
                  </div>

                  <div class="time-range-container">
                    <div class="time-field">
                      <label class="form-label">Hora de inicio</label>
                      <v-select 
                        v-model="form.horaInicio" 
                        :items="scheduleOptions" 
                        variant="outlined"
                        density="comfortable" 
                        hide-details 
                        class="custom-input"
                        @update:model-value="resetHoraFin"
                      ></v-select>
                    </div>
                    <div class="time-field">
                      <label class="form-label">Hora de fin</label>
                      <v-select 
                        v-model="form.horaFin" 
                        :items="horasFinDisponibles" 
                        variant="outlined"
                        density="comfortable" 
                        hide-details 
                        class="custom-input" 
                        :disabled="!form.horaInicio"
                        placeholder="Primero selecciona hora de inicio"
                      ></v-select>
                    </div>
                  </div>

                  <div class="form-submit">
                    <v-btn 
                      type="submit" 
                      class="submit-btn primary-btn"
                      :loading="isSubmittingAreaComun"
                      :disabled="isSubmittingAreaComun"
                    >
                      <i v-if="!isSubmittingAreaComun" class="fas fa-paper-plane"></i>
                      {{ isSubmittingAreaComun ? 'Enviando...' : 'Enviar solicitud' }}
                    </v-btn>
                  </div>
                </v-form>
              </div>
            </v-tabs-window-item>
          </v-tabs-window>
        </div>
      </div>

      <div class="table-column">
        <div class="table-card">
          <div class="table-header">
            <h2 class="table-title">Historial de solicitudes</h2>
          </div>

          <div class="search-filter-container">
            <div class="search-container">
              <i class="fas fa-search search-icon"></i>
              <input
                v-model="searchTerm"
                type="text"
                placeholder="Buscar por motivo..."
                class="search-input"
              />
            </div>
            <div class="select-container">
              <select
                v-model="selectedFilterTab"
                class="filter-select"
              >
                <option value="todos">Todos</option>
                <option value="Aprobado">Aprobados</option>
                <option value="En revisión">Pendientes</option>
                <option value="Denegado">Denegados</option>
              </select>
              <i class="fas fa-chevron-down select-icon"></i>
            </div>
          </div>

          <div v-if="activeTab === 'solicitud'" class="solicitudes-list">
            <div v-if="filteredSolicitudesDisplay.length === 0" class="empty-state">
              <i class="fas fa-exclamation-circle empty-icon"></i>
              <p class="empty-text">No se encontraron solicitudes</p>
            </div>
            <div 
              v-else
              v-for="solicitud in filteredSolicitudesDisplay" 
              :key="solicitud.id"
              class="solicitud-card"
              @click="viewDetails(solicitud)"
            >
              <div class="solicitud-header">
                <div class="solicitud-info">
                  <div class="solicitud-status-row">
                    <span :class="getStatusBadgeClass(solicitud.estado)" class="status-badge">
                      <i :class="getStatusIcon(solicitud.estado)"></i>
                      {{ solicitud.estado }}
                    </span>
                    <span class="solicitud-id">ID: #{{ solicitud.id }}</span>
                  </div>
                  <p class="solicitud-motivo">{{ solicitud.motivo || 'Sin motivo especificado' }}</p>
                  <div class="solicitud-dates">
                    <span class="date-item">
                      <i class="fas fa-calendar"></i>
                      {{ formatDate(solicitud.fecha_salida) }}
                    </span>
                    <span class="date-separator">→</span>
                    <span class="date-item">
                      <i class="fas fa-calendar"></i>
                      {{ formatDate(solicitud.fecha_regreso) }}
                    </span>
                  </div>
                </div>
                <div class="solicitud-actions">
                  <button 
                    v-if="solicitud.archivo_url" 
                    @click.stop="downloadFile(solicitud.archivo_url)"
                    class="action-button download-btn"
                  >
                    <i class="fas fa-download"></i>
                  </button>
                  <button class="action-button view-btn">
                    <i class="fas fa-eye"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeTab === 'area-comun'" class="solicitudes-list">
            <div v-if="filteredAreaComunDisplay.length === 0" class="empty-state">
              <i class="fas fa-exclamation-circle empty-icon"></i>
              <p class="empty-text">No se encontraron reservas</p>
            </div>
            <div 
              v-else
              v-for="reserva in filteredAreaComunDisplay" 
              :key="reserva.id"
              class="solicitud-card"
              @click="viewDetailsAreaComun(reserva)"
            >
              <div class="solicitud-header">
                <div class="solicitud-info">
                  <div class="solicitud-status-row">
                    <span :class="getStatusBadgeClass(reserva.estado)" class="status-badge">
                      <i :class="getStatusIcon(reserva.estado)"></i>
                      {{ reserva.estado }}
                    </span>
                    <span class="solicitud-id">ID: #{{ reserva.id }}</span>
                  </div>
                  <p class="solicitud-motivo">{{ reserva.motivo || 'Sin motivo especificado' }}</p>
                  <div class="solicitud-dates">
                    <span class="date-item">
                      <i class="fas fa-map-marker-alt"></i>
                      {{ reserva.lugar }}
                    </span>
                    <span class="date-separator">•</span>
                    <span class="date-item">
                      <i class="fas fa-calendar"></i>
                      {{ formatDate(reserva.fecha) }}
                    </span>
                    <span class="date-separator">•</span>
                    <span class="date-item">
                      <i class="fas fa-clock"></i>
                      {{ reserva.horario }}
                    </span>
                  </div>
                </div>
                <div class="solicitud-actions">
                  <button class="action-button view-btn">
                    <i class="fas fa-eye"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="currentTotalPages > 1" class="pagination-container">
            <div class="pagination-info">
              <label class="pagination-label">Mostrar:</label>
              <select
                v-model="currentItemsPerPage"
                @change="currentPage = 1"
                class="pagination-select"
              >
                <option :value="5">5</option>
                <option :value="10">10</option>
                <option :value="20">20</option>
              </select>
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
                {{ currentPage }} de {{ currentTotalPages }}
              </span>
              
              <button
                @click="currentPage = Math.min(currentPage + 1, currentTotalPages)"
                :disabled="currentPage === currentTotalPages"
                class="pagination-btn"
              >
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </ContainerView>

  <!-- Snackbar para estudiantes -->
  <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000" location="top">
    {{ snackbar.message }}
    <template v-slot:actions>
      <v-btn variant="text" @click="snackbar.show = false"> Cerrar </v-btn>
    </template>
  </v-snackbar>

  <!-- Vista para administradores -->
  <ContainerView v-if="isAdmin">
    <v-tabs v-model="adminTab" align-tabs="start" color="#A37801">
      <v-tab value="permisos-salida" class="custom-tab">
        <h4>Permisos de Salida</h4>
      </v-tab>
      <v-tab value="area-comun" class="custom-tab">
        <h4>Área Común</h4>
      </v-tab>
    </v-tabs>

    <v-tabs-window v-model="adminTab">
      <v-tabs-window-item value="permisos-salida">
        <div class="dashboard-cards mb-6 mt-6">
          <div class="stat-card">
            <div class="stat-icon blue">
              <i class="fas fa-calendar-alt"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Total Solicitudes</p>
              <p class="stat-value">{{ solicitudes.length }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon yellow">
              <i class="fas fa-clock"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">En Revisión</p>
              <p class="stat-value">{{solicitudes.filter(p => p.estado === 'En revisión').length}}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon green">
              <i class="fas fa-check"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Aprobados</p>
              <p class="stat-value">{{solicitudes.filter(p => p.estado === 'Aprobado').length}}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon red">
              <i class="fas fa-times"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Rechazados</p>
              <p class="stat-value">{{solicitudes.filter(p => p.estado === 'Denegado').length}}</p>
            </div>
          </div>
        </div>

        <div class="search-filter-section">
          <div class="search-input-container">
            <i class="fas fa-search search-icon"></i>
            <input type="text" placeholder="Buscar por nombre o motivo..." class="search-input" v-model="searchTerm" />
          </div>
          <div class="filter-tabs">
            <button v-for="tab in filterTabs" :key="tab.value" @click="selectedFilterTab = tab.value"
              :class="['filter-tab', { 'active': selectedFilterTab === tab.value }]">
              {{ tab.label }}
            </button>
          </div>
        </div>

        <div class="permisos-table-container">
          <div class="table-wrapper">
            <table class="permisos-table">
              <thead>
                <tr>
                  <th>Residente</th>
                  <th>Fechas</th>
                  <th>Duración</th>
                  <th>Motivo</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="permiso in filteredSolicitudes" :key="permiso.id" class="table-row">
                  <td>
                    <div class="employee-info">
                      <div class="avatar">
                        {{ getInitials(permiso.nombre_usuario) }}
                      </div>
                      <div class="employee-details">
                        <div class="employee-name">{{ permiso.nombre_usuario }}</div>
                        <div class="employee-id">ID: {{ permiso.id }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="date-info">
                      <div class="date-range">
                        {{ dateFormatV2(permiso.fecha_salida) }} - {{ dateFormatV2(permiso.fecha_regreso) }}
                      </div>
                      <div class="date-requested" v-if="permiso.Fecha_solicitada">
                        Solicitado: {{ dateFormatISO(permiso.Fecha_solicitada) }}
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="duration">
                      {{ calculateDays(permiso.fecha_salida, permiso.fecha_regreso) }} días
                    </div>
                  </td>
                  <td>
                    <div class="motivo" :title="permiso.motivo">
                      {{ permiso.motivo || 'Sin motivo' }}
                    </div>
                  </td>
                  <td>
                    <span :class="['status-badge', getStatusClass(permiso.estado)]">
                      <i :class="getStatusIcon(permiso.estado)"></i>
                      {{ permiso.estado }}
                    </span>
                  </td>
                  <td>
                    <div class="actions">
                      <button v-if="permiso.archivo_justificacion" @click="downloadFile(permiso.archivo_justificacion)" 
                        class="action-btn download" title="Descargar archivo">
                        <i class="fas fa-download"></i>
                      </button>
                      <button @click="viewDetails(permiso)" class="action-btn view" title="Ver detalles">
                        <i class="fas fa-eye"></i>
                      </button>
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
            <span>de {{ totalFilteredItems }} resultados</span>
          </div>
          <div class="pagination-controls">
            <button @click="currentPage = Math.max(currentPage - 1, 1)" :disabled="currentPage === 1"
              class="pagination-btn">
              <i class="fas fa-chevron-left"></i>
            </button>
            <span class="pagination-text">
              Página {{ currentPage }} de {{ totalPages }}
            </span>
            <button @click="currentPage = Math.min(currentPage + 1, totalPages)" :disabled="currentPage === totalPages"
              class="pagination-btn">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </v-tabs-window-item>

      <v-tabs-window-item value="area-comun">
        <div class="dashboard-cards mb-6 mt-6">
          <div class="stat-card">
            <div class="stat-icon blue">
              <i class="fas fa-calendar-alt"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Total Reservas</p>
              <p class="stat-value">{{ areaComunItems.length }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon yellow">
              <i class="fas fa-clock"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">En Revisión</p>
              <p class="stat-value">{{areaComunItems.filter(p => p.estado === 'En revisión').length}}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon green">
              <i class="fas fa-check"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Aprobados</p>
              <p class="stat-value">{{areaComunItems.filter(p => p.estado === 'Aprobado').length}}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon red">
              <i class="fas fa-times"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Rechazados</p>
              <p class="stat-value">{{areaComunItems.filter(p => p.estado === 'Denegado').length}}</p>
            </div>
          </div>
        </div>

        <div class="search-filter-section">
          <div class="search-input-container">
            <i class="fas fa-search search-icon"></i>
            <input type="text" placeholder="Buscar por nombre o lugar..." class="search-input"
              v-model="searchTermAreaComun" />
          </div>
          <div class="filter-tabs">
            <button v-for="tab in filterTabs" :key="tab.value" @click="selectedFilterTabAreaComun = tab.value"
              :class="['filter-tab', { 'active': selectedFilterTabAreaComun === tab.value }]">
              {{ tab.label }}
            </button>
          </div>
        </div>

        <div class="permisos-table-container">
          <div class="table-wrapper">
            <table class="permisos-table">
              <thead>
                <tr>
                  <th>Empleado</th>
                  <th>Lugar y Fecha</th>
                  <th>Horario</th>
                  <th>Motivo</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="permiso in filteredAreaComun" :key="permiso.id" class="table-row">
                  <td>
                    <div class="employee-info">
                      <div class="avatar">
                        {{ getInitials(permiso.nombre_usuario) }}
                      </div>
                      <div class="employee-details">
                        <div class="employee-name">{{ permiso.nombre_usuario }}</div>
                        <div class="employee-id">ID: {{ permiso.id }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="lugar-info">
                      <div class="lugar-nombre">
                        <i class="fas fa-map-marker-alt" style="color: #53696D; margin-right: 8px;"></i>
                        {{ permiso.lugar }}
                      </div>
                      <div class="lugar-fecha">
                        {{ dateFormatV2(permiso.fecha) }}
                      </div>
                      <div class="date-requested" v-if="permiso.Fecha_solicitada">
                        Solicitado: {{ dateFormatISO(permiso.Fecha_solicitada) }}
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="horario-info">
                      <i class="fas fa-clock" style="color: #53696D; margin-right: 8px;"></i>
                      {{ permiso.horario }}
                    </div>
                  </td>
                  <td>
                    <div class="motivo" :title="permiso.motivo">
                      {{ permiso.motivo || 'Sin motivo' }}
                    </div>
                  </td>
                  <td>
                    <span :class="['status-badge', getStatusClass(permiso.estado)]">
                      <i :class="getStatusIcon(permiso.estado)"></i>
                      {{ permiso.estado }}
                    </span>
                  </td>
                  <td>
                    <div class="actions">
                      <button @click="viewDetailsAreaComun(permiso)" class="action-btn view" title="Ver detalles">
                        <i class="fas fa-eye"></i>
                      </button>
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
            <select v-model="itemsPerPageAreaComun" class="items-select">
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="25">25</option>
              <option value="50">50</option>
            </select>
            <span>de {{ totalFilteredItemsAreaComun }} resultados</span>
          </div>
          <div class="pagination-controls">
            <button @click="currentPageAreaComun = Math.max(currentPageAreaComun - 1, 1)"
              :disabled="currentPageAreaComun === 1" class="pagination-btn">
              <i class="fas fa-chevron-left"></i>
            </button>
            <span class="pagination-text">
              Página {{ currentPageAreaComun }} de {{ totalPagesAreaComun }}
            </span>
            <button @click="currentPageAreaComun = Math.min(currentPageAreaComun + 1, totalPagesAreaComun)"
              :disabled="currentPageAreaComun === totalPagesAreaComun" class="pagination-btn">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </v-tabs-window-item>
    </v-tabs-window>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000" location="top">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false"> Cerrar </v-btn>
      </template>
    </v-snackbar>
  </ContainerView>

  <ModalDetallePermiso v-model="showModalDetalle" :permiso="selectedPermiso" :is-admin="isAdmin"
    @estado-actualizado="onEstadoActualizado" />

  <ModalDetalleAreaComun v-model="showModalDetalleAreaComun" :reserva="selectedPermisoAreaComun" :is-admin="isAdmin"
    @estado-actualizado="onEstadoActualizadoAreaComun" />
</template>
<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { dateFormatV2, dateFormatISO } from '@/util/functions.js'
import LoginService from '@/services/LoginService'
import PermisosService from '@/services/PermisosService'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import ContainerView from '@/components/layout/ContainerView.vue'
import ModalDetallePermiso from './modal/ModalDetallePermiso.vue'
import ModalDetalleAreaComun from './modal/ModalDetalleAreaComun.vue'

const solicitudes = ref([])
const areaComunItems = ref([])
const activeTab = ref('solicitud')
const adminTab = ref('permisos-salida')
const user = ref(LoginService.getCurrentUser())
const isAdmin = LoginService.isAdmin()
const searchTerm = ref('')
const selectedFilterTab = ref('todos')
const currentPage = ref(1)
const itemsPerPage = ref(10)
const selectedPermiso = ref(null)
const showModalDetalle = ref(false)

const searchTermAreaComun = ref('')
const selectedFilterTabAreaComun = ref('todos')
const currentPageAreaComun = ref(1)
const itemsPerPageAreaComun = ref(10)
const selectedPermisoAreaComun = ref(null)
const showModalDetalleAreaComun = ref(false)

const form = reactive({
  rangoFechas: null,
  motivo: '',
  lugar: '',
  fechaAreaComun: null,
  horaInicio: '',
  horaFin: '',
  fechaSalida: null,
  fechaRegreso: null,
  motivoAreaComun: ''
})

const fileInputSalida = ref(null)
const selectedFileSalida = ref(null)
const isSubmittingSalida = ref(false)
const isSubmittingAreaComun = ref(false)
const snackbar = reactive({ show: false, message: '', color: 'success' })

const filterTabs = [
  { value: 'todos', label: 'Todos' },
  { value: 'pendientes', label: 'Pendientes' },
  { value: 'aprobados', label: 'Aprobados' },
  { value: 'rechazados', label: 'Rechazados' }
]
const siteOptions = [
  'Hall',
  'patio',
  'Lavandería',
  'Sala de cómputo'
]
const scheduleOptions = [
  '9:00 AM',
  '10:00 AM',
  '11:00 AM',
  '12:00 PM',
  '1:00 PM',
  '2:00 PM',
  '3:00 PM',
  '4:00 PM',
  '5:00 PM',
  '6:00 PM',
  '7:00 PM',
  '8:00 PM'
]

const horasFinDisponibles = computed(() => {
  if (!form.horaInicio) {
    return []
  }

  const indiceInicio = scheduleOptions.findIndex(hora => hora === form.horaInicio)
  if (indiceInicio === -1) {
    return []
  }

  return scheduleOptions.slice(indiceInicio + 1)
})

const filteredSolicitudes = computed(() => {
  const filtered = solicitudes.value.filter(permiso => {
    const matchesSearch = permiso.nombre_usuario?.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      permiso.motivo?.toLowerCase().includes(searchTerm.value.toLowerCase())

    const matchesTab = selectedFilterTab.value === 'todos' ||
      (selectedFilterTab.value === 'pendientes' && permiso.estado === 'En revisión') ||
      (selectedFilterTab.value === 'aprobados' && permiso.estado === 'Aprobado') ||
      (selectedFilterTab.value === 'rechazados' && permiso.estado === 'Denegado')

    return matchesSearch && matchesTab
  })

  const startIndex = (currentPage.value - 1) * itemsPerPage.value
  return filtered.slice(startIndex, startIndex + itemsPerPage.value)
})

const totalFilteredItems = computed(() => {
  return solicitudes.value.filter(permiso => {
    const matchesSearch = permiso.nombre_usuario?.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      permiso.motivo?.toLowerCase().includes(searchTerm.value.toLowerCase())

    const matchesTab = selectedFilterTab.value === 'todos' ||
      (selectedFilterTab.value === 'pendientes' && permiso.estado === 'En revisión') ||
      (selectedFilterTab.value === 'aprobados' && permiso.estado === 'Aprobado') ||
      (selectedFilterTab.value === 'rechazados' && permiso.estado === 'Denegado')

    return matchesSearch && matchesTab
  }).length
})

const totalPages = computed(() => {
  return Math.ceil(totalFilteredItems.value / itemsPerPage.value)
})

const filteredAreaComun = computed(() => {
  const filtered = areaComunItems.value.filter(permiso => {
    const matchesSearch = permiso.nombre_usuario?.toLowerCase().includes(searchTermAreaComun.value.toLowerCase()) ||
      permiso.lugar?.toLowerCase().includes(searchTermAreaComun.value.toLowerCase()) ||
      permiso.motivo?.toLowerCase().includes(searchTermAreaComun.value.toLowerCase())

    const matchesTab = selectedFilterTabAreaComun.value === 'todos' ||
      (selectedFilterTabAreaComun.value === 'pendientes' && permiso.estado === 'En revisión') ||
      (selectedFilterTabAreaComun.value === 'aprobados' && permiso.estado === 'Aprobado') ||
      (selectedFilterTabAreaComun.value === 'rechazados' && permiso.estado === 'Denegado')

    return matchesSearch && matchesTab
  })

  const startIndex = (currentPageAreaComun.value - 1) * itemsPerPageAreaComun.value
  return filtered.slice(startIndex, startIndex + itemsPerPageAreaComun.value)
})

const totalFilteredItemsAreaComun = computed(() => {
  return areaComunItems.value.filter(permiso => {
    const matchesSearch = permiso.nombre_usuario?.toLowerCase().includes(searchTermAreaComun.value.toLowerCase()) ||
      permiso.lugar?.toLowerCase().includes(searchTermAreaComun.value.toLowerCase()) ||
      permiso.motivo?.toLowerCase().includes(searchTermAreaComun.value.toLowerCase())

    const matchesTab = selectedFilterTabAreaComun.value === 'todos' ||
      (selectedFilterTabAreaComun.value === 'pendientes' && permiso.estado === 'En revisión') ||
      (selectedFilterTabAreaComun.value === 'aprobados' && permiso.estado === 'Aprobado') ||
      (selectedFilterTabAreaComun.value === 'rechazados' && permiso.estado === 'Denegado')

    return matchesSearch && matchesTab
  }).length
})

const totalPagesAreaComun = computed(() => {
  return Math.ceil(totalFilteredItemsAreaComun.value / itemsPerPageAreaComun.value)
})

const filteredSolicitudesDisplay = computed(() => {
  const filtered = solicitudes.value.filter(item => {
    const matchesSearch = item.motivo?.toLowerCase().includes(searchTerm.value.toLowerCase()) || false
    const matchesTab = selectedFilterTab.value === 'todos' || item.estado === selectedFilterTab.value
    return matchesSearch && matchesTab
  })

  const startIndex = (currentPage.value - 1) * itemsPerPage.value
  return filtered.slice(startIndex, startIndex + itemsPerPage.value)
})

const filteredAreaComunDisplay = computed(() => {
  const filtered = areaComunItems.value.filter(item => {
    const matchesSearch = item.motivo?.toLowerCase().includes(searchTerm.value.toLowerCase()) || 
                         item.lugar?.toLowerCase().includes(searchTerm.value.toLowerCase()) || 
                         item.nombre_usuario?.toLowerCase().includes(searchTerm.value.toLowerCase()) || false
    const matchesTab = selectedFilterTab.value === 'todos' || item.estado === selectedFilterTab.value
    return matchesSearch && matchesTab
  })

  const startIndex = (currentPage.value - 1) * itemsPerPage.value
  return filtered.slice(startIndex, startIndex + itemsPerPage.value)
})

const currentTotalPages = computed(() => {
  if (activeTab.value === 'solicitud') {
    const totalFiltered = solicitudes.value.filter(item => {
      const matchesSearch = item.motivo?.toLowerCase().includes(searchTerm.value.toLowerCase()) || false
      const matchesTab = selectedFilterTab.value === 'todos' || item.estado === selectedFilterTab.value
      return matchesSearch && matchesTab
    }).length
    return Math.ceil(totalFiltered / itemsPerPage.value)
  } else {
    const totalFiltered = areaComunItems.value.filter(item => {
      const matchesSearch = item.motivo?.toLowerCase().includes(searchTerm.value.toLowerCase()) || 
                           item.lugar?.toLowerCase().includes(searchTerm.value.toLowerCase()) || 
                           item.nombre_usuario?.toLowerCase().includes(searchTerm.value.toLowerCase()) || false
      const matchesTab = selectedFilterTab.value === 'todos' || item.estado === selectedFilterTab.value
      return matchesSearch && matchesTab
    }).length
    return Math.ceil(totalFiltered / itemsPerPage.value)
  }
})

const currentItemsPerPage = computed({
  get: () => itemsPerPage.value,
  set: (value) => {
    itemsPerPage.value = value
  }
})

watch([itemsPerPage, selectedFilterTab, searchTerm], () => {
  currentPage.value = 1
})

watch(totalPages, (newTotalPages) => {
  if (currentPage.value > newTotalPages && newTotalPages > 0) {
    currentPage.value = newTotalPages
  }
})

watch([itemsPerPageAreaComun, selectedFilterTabAreaComun, searchTermAreaComun], () => {
  currentPageAreaComun.value = 1
})

watch(totalPagesAreaComun, (newTotalPages) => {
  if (currentPageAreaComun.value > newTotalPages && newTotalPages > 0) {
    currentPageAreaComun.value = newTotalPages
  }
})

watch(() => form.fechaSalida, (newFechaSalida, oldFechaSalida) => {
  if (newFechaSalida !== oldFechaSalida && form.fechaRegreso) {
    const fechaSalida = new Date(newFechaSalida)
    const fechaRegreso = new Date(form.fechaRegreso)
    if (fechaRegreso <= fechaSalida) {
      form.fechaRegreso = null
    }
  }
})

watch(activeTab, () => {
  currentPage.value = 1
  searchTerm.value = ''
  selectedFilterTab.value = 'todos'
})

const getInitials = (name) => {
  if (!name) return '??'
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const getStatusClass = (estado) => {
  switch (estado) {
    case 'Aprobado':
      return 'approved'
    case 'Denegado':
      return 'rejected'
    case 'En revisión':
      return 'pending'
    default:
      return 'default'
  }
}

const getStatusIcon = (estado) => {
  switch (estado) {
    case 'Aprobado':
      return 'fas fa-check'
    case 'Denegado':
      return 'fas fa-times'
    case 'En revisión':
      return 'fas fa-clock'
    default:
      return 'fas fa-question-circle'
  }
}

const calculateDays = (startDate, endDate) => {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffTime = Math.abs(end - start)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
  return diffDays
}

const viewDetails = (permiso) => {
  selectedPermiso.value = permiso
  showModalDetalle.value = true
}

const viewDetailsAreaComun = (permiso) => {
  selectedPermisoAreaComun.value = permiso
  showModalDetalleAreaComun.value = true
}

const onEstadoActualizado = async ({ id, estado }) => {
  try {
    await actualizarEstadoSalida(id, estado)
    showModalDetalle.value = false
  } catch (error) {
    console.error('Error al actualizar estado desde modal:', error)
    showModalDetalle.value = false
  }
}

const onEstadoActualizadoAreaComun = async ({ id, estado }) => {
  try {
    await actualizarEstadoAreaComun(id, estado)
    showModalDetalleAreaComun.value = false
  } catch (error) {
    console.error('Error al actualizar estado área común desde modal:', error)
    showModalDetalleAreaComun.value = false
  }
}

const resetHoraFin = () => {
  if (form.horaFin) {
    const indiceInicio = scheduleOptions.findIndex(hora => hora === form.horaInicio)
    const indiceFin = scheduleOptions.findIndex(hora => hora === form.horaFin)

    if (indiceFin <= indiceInicio) {
      form.horaFin = ''
    }
  }
}

onMounted(async () => {
  await chooosePermisosDeSalida()
  await chooosePermisosDeAreaComun()
})

const triggerFileInputSalida = () => {
  fileInputSalida.value?.click()
}

const handleFileSelectSalida = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFileSalida.value = file
  }
}

const getStatusBadgeClass = (estado) => {
  switch (estado) {
    case 'Aprobado':
      return 'status-approved'
    case 'Denegado':
      return 'status-rejected'
    case 'En revisión':
      return 'status-pending'
    default:
      return 'status-default'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', { 
    day: '2-digit', 
    month: 'short', 
    year: 'numeric' 
  })
}

const getStatusColor = (estado) => {
  switch (estado) {
    case 'Aprobado':
      return 'success'
    case 'Denegado':
      return 'error'
    case 'En revisión':
      return 'warning'
    default:
      return 'grey'
  }
}

const deleteReserva = (id) => {
  if (confirm('¿Estás seguro de que quieres eliminar esta reserva?')) {
    const index = solicitudes.value.findIndex((r) => r.id === id)
    if (index > -1) {
      solicitudes.value.splice(index, 1)
      snackbar.message = 'Reserva eliminada'
      snackbar.color = 'info'
      snackbar.show = true
    }
  }
}

async function actualizarEstadoSalida(id, estado) {
  try {
    await PermisosService.actualizarEstadoPermisoSalida(id, estado)
    const permiso = solicitudes.value.find(p => p.id === id)
    if (permiso) {
      permiso.estado = estado
    }

    await chooosePermisosDeSalida()

    snackbar.message = `Permiso de salida ${estado.toLowerCase()} exitosamente`
    snackbar.color = estado === 'Aprobado' ? 'success' : 'warning'
    snackbar.show = true
  } catch (error) {
    snackbar.message = 'Error al actualizar el estado del permiso'
    snackbar.color = 'error'
    snackbar.show = true
  }
}

async function actualizarEstadoAreaComun(id, estado) {
  try {
    await PermisosService.actualizarEstadoPermisoAreaComun(id, estado)
    const permiso = areaComunItems.value.find(p => p.id === id)
    if (permiso) {
      permiso.estado = estado
    }

    await chooosePermisosDeAreaComun()

    snackbar.message = `Permiso de área común ${estado.toLowerCase()} exitosamente`
    snackbar.color = estado === 'Aprobado' ? 'success' : 'warning'
    snackbar.show = true
  } catch (error) {
    snackbar.message = 'Error al actualizar el estado del permiso'
    snackbar.color = 'error'
    snackbar.show = true
  }
}

async function submitSolicitudVivienda() {
  if (!form.fechaSalida || !form.fechaRegreso || !form.motivo) {
    snackbar.message = 'Por favor completa todos los campos'
    snackbar.color = 'error'
    snackbar.show = true
    return
  }

  isSubmittingSalida.value = true

  try {
    const fechaDesde = form.fechaSalida instanceof Date
      ? form.fechaSalida.toISOString().slice(0, 10)
      : form.fechaSalida

    const fechaHasta = form.fechaRegreso instanceof Date
      ? form.fechaRegreso.toISOString().slice(0, 10)
      : form.fechaRegreso

    const formData = new FormData()
    formData.append('id_usuario', user.value.id)
    formData.append('fecha_salida', fechaDesde)
    formData.append('fecha_regreso', fechaHasta)
    formData.append('motivo', form.motivo)

    if (selectedFileSalida.value) {
      formData.append('archivo', selectedFileSalida.value)
    }

    await PermisosService.crearPermisoSalida(formData)
    await loadPermisosDeSalidaPorUsuario()
    
    form.fechaSalida = null
    form.fechaRegreso = null
    form.motivo = ''
    selectedFileSalida.value = null
    
    snackbar.message = 'Solicitud enviada exitosamente'
    snackbar.color = 'success'
    snackbar.show = true
  } catch (error) {
    console.error('Error al enviar solicitud:', error)
    snackbar.message = 'Error al enviar la solicitud. Por favor, inténtalo de nuevo.'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    isSubmittingSalida.value = false
  }
}

async function submitAreaComun() {
  if (!form.lugar || !form.fechaAreaComun || !form.horaInicio || !form.horaFin || !form.motivoAreaComun) {
    snackbar.message = 'Por favor completa todos los campos'
    snackbar.color = 'error'
    snackbar.show = true
    return
  }

  isSubmittingAreaComun.value = true

  try {
    const fecha = form.fechaAreaComun instanceof Date
      ? form.fechaAreaComun.toISOString().slice(0, 10)
      : form.fechaAreaComun

    const horario = `${form.horaInicio} a ${form.horaFin}`

    const params = {
      id_usuario: user.value.id,
      lugar: form.lugar,
      fecha: fecha,
      horario: horario,
      motivo: form.motivoAreaComun
    }

    await PermisosService.crearPermisoAreaComun(params)
    await loadPermisosDeAreaComunPorUsuario()

    form.lugar = ''
    form.fechaAreaComun = null
    form.horaInicio = ''
    form.horaFin = ''
    form.motivoAreaComun = ''

    snackbar.message = 'Reserva enviada exitosamente'
    snackbar.color = 'success'
    snackbar.show = true
  } catch (error) {
    console.error('Error al enviar reserva:', error)
    snackbar.message = 'Error al enviar la reserva'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    isSubmittingAreaComun.value = false
  }
}

function chooosePermisosDeSalida() {
  if (LoginService.isAdmin()) {
    return loadPermisosDeSalida()
  } else {
    return loadPermisosDeSalidaPorUsuario()
  }
}

function chooosePermisosDeAreaComun() {
  if (LoginService.isAdmin()) {
    return loadPermisosDeAreaComun()
  } else {
    return loadPermisosDeAreaComunPorUsuario()
  }
}

async function loadPermisosDeSalidaPorUsuario() {
  const items = await PermisosService.obtenerPermisosDeSalidaPorUsuario(user.value.id)
  solicitudes.value = items.map((a) => ({
    estado: a.estado,
    fecha_regreso: a.fecha_regreso,
    fecha_salida: a.fecha_salida,
    id: a.id,
    id_usuario: a.id_usuario,
    motivo: a.motivo || '',
    nombre_usuario: a.nombre_usuario || user.value.nombre || 'Usuario',
    archivo_justificacion: a.archivo_justificacion,
    Fecha_solicitada: a.Fecha_solicitada,
  }))
}

async function loadPermisosDeSalida() {
  const items = await PermisosService.obtenerTodosLosPermisosDeSalida()
  solicitudes.value = items.map((a) => ({
    estado: a.estado,
    fecha_regreso: a.fecha_regreso,
    fecha_salida: a.fecha_salida,
    id: a.id,
    id_usuario: a.id_usuario,
    motivo: a.motivo || '',
    nombre_usuario: a.nombre_usuario || 'Desconocido',
    archivo_justificacion: a.archivo_justificacion,
    Fecha_solicitada: a.Fecha_solicitada,
  }))
}

async function loadPermisosDeAreaComunPorUsuario() {
  const items = await PermisosService.obtenerPermisosDeAreaComunPorUsuario(user.value.id)
  areaComunItems.value = items.map((a) => ({
    estado: a.estado,
    fecha: a.fecha,
    horario: a.horario,
    id: a.id,
    id_usuario: a.id_usuario,
    lugar: a.lugar || '',
    motivo: a.motivo || '',
    nombre_usuario: a.nombre_usuario || user.value.nombre || 'Usuario',
    Fecha_solicitada: a.Fecha_solicitada,
  }))
}

async function loadPermisosDeAreaComun() {
  const items = await PermisosService.obtenerTodosLosPermisosDeAreaComun()
  areaComunItems.value = items.map((a) => ({
    estado: a.estado,
    fecha: a.fecha,
    horario: a.horario,
    id: a.id,
    id_usuario: a.id_usuario,
    lugar: a.lugar || '',
    motivo: a.motivo || '',
    nombre_usuario: a.nombre_usuario || 'Desconocido',
    Fecha_solicitada: a.Fecha_solicitada,
  }))
}

function getButtonClass(accion, estadoActual) {
  const baseClass = 'action-button'

  if (estadoActual === 'En revisión') {
    return `${baseClass} action-button-enabled`
  }

  if (estadoActual === accion) {
    return accion === 'Aprobado'
      ? `${baseClass} action-button-approved`
      : `${baseClass} action-button-denied`
  }

  return `${baseClass} action-button-disabled`
}

function getIconStyle(accion, estadoActual) {
  if (estadoActual === 'En revisión') {
    return 'color: #666666; font-size: 16px;'
  }

  if (estadoActual === accion) {
    return 'color: white; font-size: 16px;'
  }

  return 'color: #666666; font-size: 16px;'
}

function downloadFile(fileName) {
  if (!fileName) return
  
  const baseUrl = 'http://localhost:5000/uploads/justificacion/'
  const fileUrl = baseUrl + fileName
  
  const link = document.createElement('a')
  link.href = fileUrl
  link.download = fileName
  link.target = '_blank'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>
<style scoped>
.custom-table-admin {
  margin-top: 32px;
}

.custom-table {
  border: none !important;
}

.custom-table thead {
  font-size: 18px;
  color: #163053;
  font-weight: 400;
}

.custom-table th {
  background-color: white !important;
}

.custom-table th:first-child {
  border-top-left-radius: 25px !important;
  border-bottom-left-radius: 25px !important;
}

.custom-table th:last-child {
  border-top-right-radius: 25px !important;
  border-bottom-right-radius: 25px !important;
}

.custom-table td {
  color: #525252;
  font-size: 16px;
  font-weight: 400;
  border: none !important;
}

.v-divider {
  border: 1px solid #D9D9D9 !important;
}

.v-data-table-footer {
  background-color: transparent !important;
  color: #525252 !important;
}

.n-data-table,
.n-data-table-tbody {
  background-color: transparent;
}

.text-title {
  color: white;
  font-size: 28px !important;
  font-size: larger;
  text-transform: none;
  font-family: 'Righteous', cursive;
}

.custom-tab {
  font-size: larger;
  color: #f5f5f5;
  text-transform: none;
  font-weight: 700;
  font-family: 'Righteous', cursive;
}

.active-tab-text {
  color: #A37801;
  font-weight: 600;
  padding-bottom: 4px;
}

.custom-select :deep(.v-field),
.custom-textarea :deep(.v-field) {
  border-radius: 8px;
  background-color: #f5f5f5;
}

.custom-select :deep(.v-field--focused),
.custom-textarea :deep(.v-field--focused) {
  background-color: white;
}

.custom-select :deep(.v-field--disabled) {
  background-color: #e0e0e0;
  opacity: 0.6;
}

.custom-alert :deep(.v-alert__content) {
  padding: 8px 0;
}

:deep(.v-tabs-slider) {
  background-color: #ffc107;
}

:deep(.v-tab--selected) {
  color: #A37801;
}

:deep(.dp__theme_light) {
  --dp-primary-color: #A80038;
  --dp-primary-text-color: #fff;
}

:deep(.dp__input) {
  height: 48px !important;
  border-radius: 8px;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
}

:deep(.dp__input:focus) {
  background-color: white;
}

.custom-datepicker {
  border-radius: 8px;
  background-color: #f5f5f5;
}

.action-button {
  width: 36px !important;
  height: 36px !important;
  border-radius: 50% !important;
  min-width: 36px !important;
}

.action-button-enabled {
  background-color: white !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

.action-button-approved {
  background-color: #4caf50 !important;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3) !important;
}

.action-button-denied {
  background-color: #f44336 !important;
  box-shadow: 0 2px 4px rgba(244, 67, 54, 0.3) !important;
}

.action-button-disabled {
  background-color: #f5f5f5 !important;
  opacity: 0.6 !important;
}

.action-button:hover.action-button-enabled {
  background-color: #f5f5f5 !important;
  transform: scale(1.05);
  transition: all 0.2s ease;
}

.action-button:disabled {
  pointer-events: none;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: transparent;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #A37801;
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-icon.blue {
  background-color: #dbeafe;
  color: #2563eb;
}

.stat-icon.yellow {
  background-color: #fef3c7;
  color: #d97706;
}

.stat-icon.green {
  background-color: #dcfce7;
  color: #16a34a;
}

.stat-icon.red {
  background-color: #fee2e2;
  color: #dc2626;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  font-weight: 500;
  color: #293a5f;
  margin: 0 0 4px 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.search-filter-section {
  background: transparent;
  border-radius: 12px;
  border: 1px solid #A37801;
  padding: 24px;
  margin-bottom: 24px;
}

.search-input-container {
  position: relative;
  margin-bottom: 16px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #111827;
  font-size: 16px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: #FFFBED;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  background: #A37801;
  color: white;
}

.filter-tab.active {
  background: #A37801;
  color: white;
}

.permisos-table-container {
  background: transparent;
  border-radius: 12px;
  border: 1px solid #A37801;
  overflow: hidden;
  margin-bottom: 24px;
}

.table-wrapper {
  overflow-x: auto;
}

.permisos-table {
  width: 100%;
  border-collapse: collapse;
}

.permisos-table thead {
  background: #FFFBED;
}

.permisos-table th {
  padding: 16px 24px;
  text-align: left;
  font-size: 12px;
  font-weight: 500;
  color: #525252;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #A37801;
}

.permisos-table th:last-child {
  text-align: right;
}

.permisos-table tbody tr {
  border-bottom: 1px solid #A37801;
  transition: background-color 0.2s ease;
}

.permisos-table tbody tr:hover {
  background: #FFFBED;
}

.permisos-table td {
  padding: 16px 24px;
  vertical-align: top;
}

.employee-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 40px;
  height: 40px;
  background: #A37801;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  margin-right: 16px;
}

.employee-details {
  flex: 1;
}

.employee-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin-bottom: 2px;
}

.employee-id {
  font-size: 12px;
  color: #111827;
}

.date-info {
  display: flex;
  flex-direction: column;
}

.date-range {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin-bottom: 2px;
}

.date-requested {
  font-size: 12px;
  color: #111827;
}

.duration {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
}

.motivo {
  font-size: 14px;
  color: #111827;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
  gap: 8px;
}

.status-badge i {
  margin-right: 4px;
  font-size: 10px;
}

.status-badge.approved {
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #991b1b;
  border-color: #fecaca;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
  border-color: #fde68a;
}

.status-badge.default {
  background: #f3f4f6;
  color: #374151;
  border-color: #d1d5db;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #111827;
}

.action-btn:hover {
  transform: scale(1.05);
}

.action-btn.view:hover {
  background: #dbeafe;
  color: #2563eb;
}

.action-btn.approve:hover {
  background: #dcfce7;
  color: #16a34a;
}

.action-btn.reject:hover {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.more:hover {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.download:hover {
  background: #dbeafe;
  color: #2563eb;
}

.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: transparent;
  border-radius: 12px;
  border: 1px solid #A37801;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
}

.items-select {
  padding: 4px 8px;
  border: 1px solid #A37801;
  border-radius: 4px;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.pagination-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #FFFBED;
  color: #6b7280;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f3f4f6;
  color: #374151;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-text {
  font-size: 14px;
  color: #374151;
}

@media (max-width: 768px) {
  .dashboard-cards {
    grid-template-columns: 1fr;
  }

  .search-filter-section {
    padding: 16px;
  }

  .filter-tabs {
    flex-wrap: wrap;
  }

  .pagination-container {
    flex-direction: column;
    gap: 16px;
  }

  .permisos-table th,
  .permisos-table td {
    padding: 12px 16px;
  }
}

.lugar-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lugar-nombre {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
}

.lugar-fecha {
  font-size: 14px;
  color: #111827;
  font-weight: 500;
}

.horario-info {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  display: flex;
  align-items: center;
}

.student-permissions-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin: 0 auto;
  padding: 24px;
  align-items: flex-start;
}

.form-column {
  background: #B8BAA3F2;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.form-card {
  padding: 32px;
}

.form-content {
  background: #EDEEE2F2;
  border-radius: 16px;
  padding: 32px;
  margin-top: 16px;
}

.form-header {
  margin-bottom: 32px;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 16px;
  color: #6b7280;
  line-height: 1.5;
}

.form-spacing {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.date-range-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  align-items: start;
}

.date-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-sublabel {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.time-range-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.time-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.duration-info {
  background: #f0daa4;
  color: #A37801;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.duration-icon {
  color: #A37801;
}

.helper-text {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f9fafb;
}

.upload-area:hover {
  border-color: #A37801;
  background: #ebddb9;
}

.upload-icon {
  color: #9ca3af;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
  display: block;
  margin-bottom: 4px;
}

.upload-helper {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.form-submit {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.submit-btn {
  min-width: 200px !important;
  height: 48px !important;
  border-radius: 12px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
  transition: all 0.2s ease !important;
}

.primary-btn {
  background: #7E271BF2 !important;
  color: white !important;
}

.primary-btn:hover {
  transform: translateY(-2px);
}

.table-column {
  background: #B8BAA3F2;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-card {
  padding: 32px;
}

.table-header {
  margin-bottom: 24px;
}

.table-title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
}

.table-subtitle {
  font-size: 16px;
  color: #6b7280;
  line-height: 1.5;
}

.search-filter-container {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-container {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  font-size: 16px;
}

.search-input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: #f9fafb;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-input:focus {
  outline: none;
  border-color: #A37801;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-select {
  padding: 12px 40px 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #f9fafb;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  width: 100%;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-container {
  position: relative;
  display: inline-block;
}

.select-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  font-size: 12px;
  pointer-events: none;
}

.solicitudes-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon {
  color: #d1d5db;
  margin-bottom: 12px;
}

.empty-text {
  color: #6b7280;
  font-size: 16px;
  margin: 0;
}

.solicitud-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;
  cursor: pointer;
  background: #EDEEE2F2;
}

.solicitud-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #A37801;
  transform: translateY(-1px);
}

.solicitud-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.solicitud-info {
  flex: 1;
}

.solicitud-status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-approved {
  background: #dcfce7;
  color: #166534;
}

.status-rejected {
  background: #fee2e2;
  color: #dc2626;
}

.status-pending {
  background: #fef3c7;
  color: #d97706;
}

.status-default {
  background: #f3f4f6;
  color: #6b7280;
}

.solicitud-id {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.solicitud-motivo {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.solicitud-dates {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6b7280;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.date-separator {
  font-weight: 600;
  color: #9ca3af;
}

.solicitud-actions {
  display: flex;
  gap: 8px;
}

.action-button {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.download-btn {
  background: #eff6ff;
  color: #2563eb;
}

.download-btn:hover {
  background: #dbeafe;
  color: #1d4ed8;
}

.view-btn {
  background: #f3f4f6;
  color: #6b7280;
}

.view-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-label {
  font-size: 14px;
  color: #6b7280;
}

.pagination-select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-text {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

@media (max-width: 1024px) {
  .student-permissions-container {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 16px;
  }
  
  .date-range-container,
  .time-range-container {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .search-filter-container {
    flex-direction: column;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .form-card,
  .table-card {
    padding: 20px;
  }
  
  .form-title,
  .table-title {
    font-size: 24px;
  }
  
  .upload-area {
    padding: 24px;
  }
  
  .solicitud-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .solicitud-actions {
    align-self: flex-end;
  }
}

.custom-input :deep(.v-field) {
  border-radius: 8px;
  background-color: #f8f9fa;
  border: 1px solid #e5e7eb;
}

.custom-input :deep(.v-field--focused) {
  background-color: white;
  border-color: #A37801;
}

.custom-input :deep(.dp__input) {
  height: 48px !important;
  border-radius: 8px;
  background-color: #f8f9fa;
  border: 1px solid #e5e7eb;
  font-size: 14px;
}

.custom-input :deep(.dp__input:focus) {
  background-color: white;
  border-color: #A37801;
}

.duration-icon {
  margin-right: 8px;
  color: #A37801;
  font-size: 14px;
}

.upload-icon {
  font-size: 40px;
  margin-bottom: 12px;
  color: #9ca3af;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  font-size: 16px;
}

.empty-icon {
  font-size: 48px !important;
  color: #d1d5db;
  margin-bottom: 12px;
}

.submit-btn i {
  margin-right: 8px;
  font-size: 14px;
}

.status-badge i {
  margin-right: 6px;
  font-size: 12px;
}

.date-item i {
  margin-right: 4px;
  font-size: 12px;
  color: #6b7280;
}

.action-button i {
  font-size: 14px;
}

.pagination-btn i {
  font-size: 16px;
  color: #6b7280;
}

.pagination-btn:hover:not(:disabled) i {
  color: #374151;
}

.duration-icon {
  font-size: 14px;
  color: #0277bd;
  margin-right: 8px;
}

.upload-icon {
  font-size: 32px;
  color: #9ca3af;
  margin-bottom: 12px;
}

.search-icon {
  font-size: 16px;
}

.empty-icon {
  font-size: 48px;
  color: #d1d5db;
  margin-bottom: 12px;
}

.status-badge i {
  font-size: 12px;
  margin-right: 4px;
}

.date-item i {
  font-size: 14px;
  margin-right: 4px;
  color: #6b7280;
}

.primary-btn i,
.secondary-btn i {
  margin-right: 8px;
  font-size: 14px;
}
</style>
