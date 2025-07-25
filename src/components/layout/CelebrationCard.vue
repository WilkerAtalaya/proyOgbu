<template>
  <n-card class="card-celebration pa-4">
    <div class="header-cc">
      <i class="fa-solid fa-cake-candles"></i>
      <p>Cumpleaños de hoy</p>
    </div>

    <n-list>
      <template v-if="cumpleanosItems.length > 0">
        <n-list-item v-for="item in cumpleanosItems" :key="item.id">
          <div style="display: flex; align-items: center; gap: 2px">
            <img :src="cake" alt="cumpleaños" style="width: 20px; height: 25px" />
            <span>¡Feliz cumpleaños, {{ item.nombre }}!</span>
          </div>
        </n-list-item>
      </template>
      <template v-else>
        <n-list-item>
          <span>No hay cumpleaños hoy</span>
        </n-list-item>
      </template>
    </n-list>
  </n-card>

  <n-card class="card-celebration pa-4">
    <div class="header-cc">
      <i class="fa-solid fa-award"></i>
      <p>Reconocimientos</p>
      <div v-if="isAdmin" class="text-right pl-6">
        <n-button style="background-color: #b28700; color:aliceblue" type="primary" @click="mostrarModal = true">Crear</n-button>
      </div>
    </div>
    <n-list>
      <n-list-item v-for="(reconocimiento, index) in reconocimientoItems" :key="index">
        <div style="display: flex; align-items: center; gap: 2px">
          <img :src="cupe" alt="cumpleaños" style="width: 20px; height: 20px" />
          <div style="display: grid">
            <span>{{ reconocimiento.descripcion }}</span>
            <span style="font-size: 12px">{{ formatDate(reconocimiento.fecha) }}</span>
          </div>
        </div>
      </n-list-item>
    </n-list>
  </n-card>
  <n-modal v-model:show="mostrarModal" title="Nuevo Reconocimiento" style="background-color: white; border-radius: 15px;">
    <div style="display: flex; flex-direction: column; gap: 12px; padding: 16px">
      <n-input
      style="height: 91px;"
        v-model:value="nuevoReconocimiento.descripcion"
        placeholder="Descripción del reconocimiento"
        type="textarea"
      />
      <n-button style="background-color: #b28700; color:aliceblue" type="primary" @click="enviarReconocimiento">Enviar</n-button>
    </div>
  </n-modal>
</template>

<script setup>
import cake from '@/assets/pngs/cake.jpg'
import cupe from '@/assets/pngs/trophy.jpg'
import { useRouter, useRoute } from 'vue-router'
import ReconocimientosService from '@/services/ReconocimientosService'
import LoginService from '@/services/LoginService'
import { onMounted, ref } from 'vue'

const router = useRouter()
const route = useRoute()
const reconocimientoItems = ref([])
const cumpleanosItems = ref([])
const isAdmin = LoginService.isAdmin()
const mostrarModal = ref(false)
const nuevoReconocimiento = ref({
  descripcion: '',
})

async function loadReconocimientos() {
  try {
    const reconocimientos = await ReconocimientosService.obtenerReconocimientos()
    reconocimientoItems.value = reconocimientos.map((a) => ({
      descripcion: a.descripcion,
      fecha: a.fecha,
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

function formatDate(fecha) {
  if (!fecha) return ''
  const partes = fecha.split('-')
  return `${partes[2]}/${partes[1]}/${partes[0]}`
}

onMounted(async () => {
  await loadReconocimientos()
  await loadCumpleanos()
})

async function enviarReconocimiento() {
  const user = LoginService.getCurrentUser()
  const body = {
    descripcion: nuevoReconocimiento.value.descripcion,
    fecha: new Date().toISOString().split('T')[0],
    id_usuario: user.id,
    id_alumno: 5
  }
  await ReconocimientosService.crearReconocimiento(body)
  reconocimientoItems.value.unshift({
    id_usuario: user.id,
    descripcion: body.descripcion,
    fecha: body.fecha,
  })
  nuevoReconocimiento.value = { descripcion: '', fecha: new Date().toISOString().split('T')[0] }
  mostrarModal.value = false
}
</script>

<style scoped>
.card-celebration {
  background-color: #eef1dc;
  border-radius: 10px;
  margin-bottom: 30px;
  box-shadow: 0px 6px 5px rgba(0, 0, 0, 0.15);
}
.card-celebration .n-list {
  background-color: transparent;
}
.n-list-item {
  padding: 3px !important;
}
.header-cc {
  background-color: white;
  color: #4d2d0b;
  padding: 5px 8px;
  border-radius: 8px;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.header-cc p {
  font-weight: 600 !important;
}
</style>
