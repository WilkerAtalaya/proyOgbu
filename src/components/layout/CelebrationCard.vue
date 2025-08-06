<template>
  <n-card class="card-celebration pa-4">
    <div class="header-cc">
      <img :src="globos" alt="globos" style="width: 42px; height: 42px" />
      <p>Cumpleaños</p>
    </div>

    <div v-if="cumpleanosItems.length > 0" class="birthday-content">
      <h4 class="birthday-subtitle">Hoy es el cumpleaños de</h4>
      <n-list>
        <n-list-item v-for="item in cumpleanosItems" :key="item.id">
          <div style="display: flex; align-items: center; gap: 8px">
            <span style="font-size: 18px">🎂</span>
            <span style="font-size: 16px; font-weight: 400; color: black;">{{ item.nombre }}</span>
          </div>
        </n-list-item>
      </n-list>
    </div>
    <div v-else class="no-birthday-content">
      <div class="empty-birthday-message">
        <p style="color: #888; font-size: 14px; margin: 0; text-align: center">
          No hay cumpleaños hoy
        </p>
      </div>
    </div>
  </n-card>

  <n-card class="card-celebration pa-4">
    <div class="header-cc">
      <img :src="cinta" alt="reconocimientos" style="width: 42px; height: 42px" />
      <p>Reconocimientos</p>
    </div>
    <n-list>
      <n-list-item v-for="(reconocimiento, index) in reconocimientoItems" :key="reconocimiento.id">
        <div class="reconocimiento-item">
          <div class="trophy-column">
            🏆
          </div>
          
          <div class="info-column">
            <div class="alumno-nombre">{{ reconocimiento.nombre }}</div>
            <div class="descripcion-text">{{ reconocimiento.descripcion }}</div>
          </div>
          
          <div class="action-column">
            <button 
              v-if="isAdmin" 
              class="delete-button"
              @click="eliminarReconocimiento(index)"
            >
              ✕
            </button>
          </div>
        </div>
      </n-list-item>
    </n-list>
  </n-card>
  <ModalReconocimiento
    v-model="modalStore.mostrarModalReconocimiento"
    :mode="false"
    @agregarReconocimiento="agregarReconocimiento"
  />
</template>

<script setup>
import globos from '@/assets/icons/globos.png'
import cinta from '@/assets/icons/cinta.png'
import { useRouter, useRoute } from 'vue-router'
import ReconocimientosService from '@/services/ReconocimientosService'
import LoginService from '@/services/LoginService'
import { onMounted, ref } from 'vue'
import ModalReconocimiento from './ModalReconocimiento.vue'
import { modalStore } from '@/stores/modalStore'

const router = useRouter()
const route = useRoute()
const reconocimientoItems = ref([])
const cumpleanosItems = ref([])
const isAdmin = LoginService.isAdmin()

async function loadReconocimientos() {
  try {
    const reconocimientos = await ReconocimientosService.obtenerReconocimientos()
    reconocimientoItems.value = reconocimientos.map((a) => ({
      id: a.id,
      descripcion: a.descripcion,
      fecha: a.fecha,
      nombre: a.nombre_alumno || 'Desconocido',
    }))
  } catch (error) {
    console.error(error)
  }
}

async function loadCumpleanos() {
  try {
    const cumpleanos = await ReconocimientosService.obtenerCumpleanos()
    cumpleanosItems.value = cumpleanos.map((a) => ({
      id: a.id,
      nombre: a.nombre,
      fecha_cumpleanos: a.fecha_cumpleaños,
    }))
  } catch (error) {
    console.error(error)
  }
}

onMounted(async () => {
  await loadReconocimientos()
  await loadCumpleanos()
})

function agregarReconocimiento() {
  loadReconocimientos()
}

async function eliminarReconocimiento(index) {
  if (!confirm('¿Estás seguro de que quieres eliminar este reconocimiento?')) {
    return
  }
  
  try {
    const reconocimiento = reconocimientoItems.value[index]
    await ReconocimientosService.eliminarReconocimiento(reconocimiento.id)
    await loadReconocimientos()
  } catch (error) {
    console.error('Error al eliminar reconocimiento:', error)
    alert('Error al eliminar el reconocimiento')
  }
}
</script>

<style scoped>
.card-celebration {
  background-color: #eef1dc;
  border-radius: 25px;
  padding: 24px 18px;
  box-shadow: 0px 10px 4px 0px #00000040;
  border: none;
  margin-bottom: 30px;
}
.card-celebration .n-list {
  background-color: transparent;
}
.n-list-item {
  padding: 3px !important;
}
.header-cc {
  background-color: white;
  color: #163053;
  padding:12px 8px;
  border-radius: 25px;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.header-cc p {
  flex: 1;
  text-align: center;
  font-size: 20px;
  font-weight: 400;
}

.birthday-content {
  margin-top: 8px;
}

.birthday-subtitle {
  color: #A61D1D;
  font-size: 16px;
  font-weight: 400;
  margin: 0 0 12px 0;
  text-align: center;
}

.no-birthday-content {
  margin-top: 16px;
  padding: 8px 0;
}

.empty-birthday-message {
  display: flex;
  justify-content: center;
}

.reconocimiento-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 8px 0;
}

.trophy-column {
  font-size: 20px;
  min-width: 30px;
  display: flex;
  justify-content: center;
}

.info-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.alumno-nombre {
  font-weight: 600;
  font-size: 14px;
  color: #163053;
}

.descripcion-text {
  font-size: 12px;
  color: #666;
  line-height: 1.3;
}

.action-column {
  min-width: 40px;
  display: flex;
  justify-content: center;
}

.delete-button {
  background: none;
  border: none;
  color: #e74c3c;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.delete-button:hover {
  color: #c0392b;
  background-color: rgba(231, 76, 60, 0.1);
}
</style>
