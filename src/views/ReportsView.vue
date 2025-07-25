<template>
  <div class="about"><h1>Mis reportes</h1></div>
  <div style="background-color: rgba(197, 199, 176, 0.95); width: 95%; padding: 20px; border-radius: 20px;">
    <div class="text-right">
      <v-btn variant="outlined" class="mb-6" @click="openModalNuevo">Nueva Queja</v-btn>
    </div>
    <v-data-table :items="filteredData"  :items-per-page="5">
      <template #headers>
        <tr>
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
              style="background: none; border: none; cursor: pointer"
              title="Ver detalle"
            >
              <i class="fa-solid fa-eye" style="color: #1976d2; font-size: 20px"></i>
            </button>
          </td>
        </tr>
      </template>
    </v-data-table>
    <ModalQueja :type="modalType" v-model="showModal" :item="selectedItem" :user="user" :mode="isView"  @agregar-queja="agregarQueja" />
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import QuejasService from '@/services/QuejasService'
import ModalQueja from './modal/ModalQueja.vue'
import LoginService from '@/services/LoginService'


const data = ref([])
const isView = ref("")
const showModal = ref(false)
const selectedItem = ref(null)
const selectedAddress = ref(null)
const modalType = ref('queja')
const user = ref(LoginService.getCurrentUser())

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
</script>
<style scoped>
.n-data-table,
.n-data-table-tbody {
  background-color: transparent;
}
</style>
