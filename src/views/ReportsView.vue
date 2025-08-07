<template>
  <ContainerView>
    <v-tabs v-model="tab" align-tabs="start" color="#A37801">
      <h3 class="mb-4 text-title">{{ isAdmin ? 'Reportes' : 'Mis reportes' }}</h3>
      <v-spacer></v-spacer>
      <v-btn v-if="!isAdmin" variant="outlined" class="mb-6 custom-button" @click="openModalNuevo">
        <span>🚨 Realizar una Queja</span>
      </v-btn>
    </v-tabs>
    <v-data-table :items="filteredData"  :items-per-page="10" class="custom-table">
      <template #headers>
        <tr class="table-header">
          <th>N° Reporte</th>
          <th>Asunto</th>
          <th>Motivo</th>
          <th>Fecha</th>
          <th>Estado</th>
          <th>Acción</th>
        </tr>
      </template>
      <template #item="{ item }">
        <tr>
          <td>{{ item.numero }}</td>
          <td>{{ item.asunto }}</td>
          <td>{{ item.motivo }}</td>
          <td>{{ item.fecha }}</td>
          <td>{{ item.estado }}</td>
          <td>
            <button
              @click="openModal(item)"
              style="background: none; border: none; cursor: pointer;"
              title="Ver detalle"
            >
              <i class="fa-solid fa-eye" style="color: #1976d2; font-size: 20px;"></i>
            </button>
          </td>
        </tr>
      </template>
    </v-data-table>
    <ModalQueja :type="modalType" v-model="showModal" :item="selectedItem" :user="user" :mode="isView"  @agregar-queja="agregarQueja" @actualizar-estado="onEstadoActualizado" />
  </ContainerView>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import QuejasService from '@/services/QuejasService'
import ModalQueja from './modal/ModalQueja.vue'
import LoginService from '@/services/LoginService'
import ContainerView from '@/components/layout/ContainerView.vue'


const data = ref([])
const isView = ref("")
const showModal = ref(false)
const selectedItem = ref(null)
const selectedAddress = ref(null)
const modalType = ref('queja')
const user = ref(LoginService.getCurrentUser())
const isAdmin = LoginService.isAdmin()

const filteredData = computed(() => {
  if (!selectedAddress.value) return data.value
  return data.value.filter((item) => item.address?.includes(selectedAddress.value))
})

onMounted(async () => {
  chooseQuejas()
})

function openModal(item) {
  selectedItem.value = item
  showModal.value = true
  isView.value = true
}

function agregarQueja(queja) {
  data.value.unshift(queja)
}

function openModalNuevo(type = 'queja') {
  selectedItem.value = {
    numero: '',
    asunto: '',
    motivo: '',
    fecha: '',
    estado: '',
    descripcion: '',
  }
  isView.value = false
  modalType.value = type
  showModal.value = true
}

async function loadQuejasPorUsuario() {
  try {
    const quejas = await QuejasService.obtenerQuejasPorUsuario(user.value.id)
    data.value = quejas.map((a) => ({
      id: a.id,
      numero: a.codigo,
      asunto: a.asunto,
      motivo: a.motivo ?? '',
      fecha: a.fecha,
      estado: a.estado,
      descripcion: a.descripcion
    }))
  } catch (error) {
    console.error(error)
  }
}

async function loadQuejas() {
  try {
    const quejas = await QuejasService.obtenerTodos()
    data.value = quejas.map((a) => ({
      id: a.id,
      numero: a.codigo,
      asunto: a.asunto,
      motivo: a.motivo ?? '',
      fecha: a.fecha,
      estado: a.estado,
      descripcion: a.descripcion
    }))
  } catch (error) {
    console.error(error)
  }
}

function chooseQuejas() {
  if (LoginService.isAdmin()) {
    loadQuejas()
  } else {
    loadQuejasPorUsuario()
  }
}

function onEstadoActualizado() {
  chooseQuejas()
}
</script>
<style scoped>
.custom-table {
  margin-top: 32px;
}
.n-data-table,
.n-data-table-tbody {
  background-color: transparent;
}

.text-title{
  color: white;
  font-size: 28px !important;
  font-size: larger;
  text-transform: none;
  font-family: 'Righteous', cursive;
}

.custom-button {
  background-color: #53696D !important;
  border-radius: 25px !important;
  border: none !important;
  padding: 16px 24px !important;
  height: auto !important;
  margin: 0 !important;
}

.custom-button span {
  color: white !important;
}
</style>
