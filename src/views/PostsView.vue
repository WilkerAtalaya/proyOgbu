<template>
  <div class="main-container">
    <div class="mobile-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <i :class="tab.icon"></i>
        {{ tab.name }}
      </button>
    </div>

    <div class="left-column">
      <ModalPublicacion
        v-model="modalStore.mostrarModalPublicacion"
        :mode="false"
        :editData="editingPost"
        @agregarPublicacion="agregarPublicacion"
        @actualizarPublicacion="actualizarPublicacion"
        @mostrar-notificacion="onMostrarNotificacion"
      />
      <ConfirmationModal
        v-model="showConfirmModal"
        title="Eliminar publicación"
        message="¿Estás seguro de que deseas eliminar esta publicación? Esta acción no se puede deshacer."
        confirmText="Eliminar"
        cancelText="Cancelar"
        confirmColor="#A80038"
        icon="fas fa-exclamation-triangle"
        iconColor="#A80038"
        @confirm="confirmarEliminacion"
        @cancel="cancelarEliminacion"
      />
      <div v-show="activeTab === 'posts'" class="posts-container">
        <div class="post-card" v-for="post in posts" :key="post.id">
          <div class="post-header">
            <div class="post-title-section">
              <h3 class="post-title">{{ post.titulo }}</h3>
              <div class="post-meta">
                <span class="post-date">{{ dateFormatISO(post.fecha_publicacion) }}</span>
              </div>
            </div>
            <div class="post-actions" v-if="isAdmin">
              <v-btn
                icon
                size="small"
                variant="text"
                class="action-btn edit-btn"
                @click="editarPublicacion(post)"
                style="color: #A80038;"
              >
                <i class="fas fa-edit"></i>
              </v-btn>
              <v-btn
                icon
                size="small"
                variant="text"
                class="action-btn delete-btn"
                @click="eliminarPublicacion(post.id)"
                style="color: #A80038;"
              >
                <i class="fas fa-trash"></i>
              </v-btn>
            </div>
          </div>

          <div class="post-content">
            <div class="post-description">{{ post.descripcion }}</div>
            <div v-if="post.archivo && post.archivo.url" class="post-image-container">
              <n-image 
                :src="post.archivo.url" 
                alt="Imagen del anuncio"
                object-fit="cover"
                :style="{ width: '100%', height: 'auto', maxHeight: '400px', borderRadius: '12px' }"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-show="activeTab === 'birthdays'" class="mobile-content">
        <div class="mobile-birthday-section">
          <div class="mobile-section-header">
            <i class="fas fa-birthday-cake"></i>
            <h2>Cumpleaños de Hoy</h2>
          </div>
          <div v-if="birthdayData.length > 0" class="birthday-list">
            <div v-for="birthday in birthdayData" :key="birthday.id" class="birthday-item">
              <span class="birthday-emoji">🎂</span>
              <span class="birthday-name">{{ birthday.nombre }}</span>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>No hay cumpleaños hoy</p>
          </div>
        </div>
      </div>

      <div v-show="activeTab === 'recognitions'" class="mobile-content">
        <div class="mobile-recognition-section">
          <div class="mobile-section-header">
            <i class="fas fa-trophy"></i>
            <h2>Reconocimientos</h2>
          </div>
          <div v-if="recognitionData.length > 0" class="recognition-list">
            <div v-for="recognition in recognitionData" :key="recognition.id" class="recognition-item">
              <div class="recognition-trophy">🏆</div>
              <div class="recognition-info">
                <div class="recognition-name">{{ recognition.nombre }}</div>
                <div class="recognition-description">{{ recognition.descripcion }}</div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>No hay reconocimientos</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="right-column">
      <img :src="logo" alt="Logo OGBU" class="logo-image" />
      <CelebrationCard />
    </div>

    <div v-if="isAdmin && isMobile" class="floating-action-buttons">
      <button 
        v-if="activeTab === 'posts'"
        @click="modalStore.mostrarModalPublicacion = true"
        class="floating-btn floating-btn-post"
      >
        <i class="fas fa-bullhorn"></i>
      </button>
      
      <button 
        v-if="activeTab === 'recognitions'"
        @click="modalStore.mostrarModalReconocimiento = true"
        class="floating-btn floating-btn-recognition"
      >
        <i class="fas fa-trophy"></i>
      </button>
    </div>
  </div>
  
  <v-snackbar 
    v-model="snackbar.show" 
    :color="snackbar.color" 
    timeout="4000"
    location="top"
  >
    {{ snackbar.message }}
    <template v-slot:actions>
      <v-btn variant="text" @click="snackbar.show = false">
        Cerrar
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script setup>
import AnunciosService from '@/services/AnunciosService'
import ReconocimientosService from '@/services/ReconocimientosService'
import { dateFormatISO } from '@/shared/util/functions.js'
import { ref, onMounted, watch, computed } from 'vue'
import LoginService from '@/services/LoginService'
import ModalPublicacion from './modal/ModalPublicacion.vue'
import logo from '@/assets/OGBU-logo.png'
import CelebrationCard from '@/components/layout/CelebrationCard.vue'
import ConfirmationModal from '@/components/layout/ConfirmationModal.vue'
import { modalStore } from '@/stores/modalStore'

const isAdmin = LoginService.isAdmin()
const posts = ref([])
const editingPost = ref(null)
const showConfirmModal = ref(false)
const postToDelete = ref(null)

const activeTab = ref('posts')
const birthdayData = ref([])
const recognitionData = ref([])

const tabs = [
  { id: 'posts', name: 'Publicaciones', icon: 'fas fa-bullhorn' },
  { id: 'birthdays', name: 'Cumpleaños', icon: 'fas fa-birthday-cake' },
  { id: 'recognitions', name: 'Reconocimientos', icon: 'fas fa-trophy' }
]

const isMobile = computed(() => window.innerWidth <= 768)

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

watch(() => modalStore.mostrarModalPublicacion, (isOpen) => {
  if (!isOpen) {
    editingPost.value = null
  }
})

async function loadPublicaciones() {
  try {
    posts.value = await AnunciosService.listarAnuncios()
  } catch (error) {
    console.error('Error al obtener anuncios:', error)
  }
}

function agregarPublicacion() {
  loadPublicaciones()
}

function actualizarPublicacion() {
  loadPublicaciones()
}

function onMostrarNotificacion({ mensaje, tipo }) {
  snackbar.value = {
    show: true,
    message: mensaje,
    color: tipo
  }
}

function editarPublicacion(post) {
  editingPost.value = post
  modalStore.mostrarModalPublicacion = true
}

function eliminarPublicacion(postId) {
  postToDelete.value = postId
  showConfirmModal.value = true
}

async function confirmarEliminacion() {
  try {
    await AnunciosService.eliminarAnuncio(postToDelete.value)
    await loadPublicaciones()
    onMostrarNotificacion({ mensaje: 'Publicación eliminada exitosamente', tipo: 'success' })
  } catch (error) {
    onMostrarNotificacion({ mensaje: 'Error al eliminar la publicación', tipo: 'error' })
  } finally {
    postToDelete.value = null
  }
}

function cancelarEliminacion() {
  postToDelete.value = null
}

async function loadBirthdayData() {
  try {
    const birthdays = await ReconocimientosService.obtenerCumpleanos()
    birthdayData.value = birthdays.map((birthday) => ({
      id: birthday.id,
      nombre: birthday.nombre,
      fecha_cumpleanos: birthday.fecha_cumpleaños,
    }))
  } catch (error) {
    console.error('Error al cargar cumpleaños:', error)
  }
}

async function loadRecognitionData() {
  try {
    const recognitions = await ReconocimientosService.obtenerReconocimientos()
    recognitionData.value = recognitions.map((recognition) => ({
      id: recognition.id,
      descripcion: recognition.descripcion,
      fecha: recognition.fecha,
      nombre: recognition.nombre_alumno || 'Desconocido',
    }))
  } catch (error) {
    console.error('Error al cargar reconocimientos:', error)
  }
}

onMounted(async () => {
  await loadPublicaciones()
  await loadBirthdayData()
  await loadRecognitionData()
})
</script>


<style scoped>
.main-container {
  display: flex;
  gap: 20px;
  min-height: 100vh;
  overflow-x: hidden;
}

.left-column {
  flex: 1;
  padding: 32px;
}

.right-column {
  width: 347px;
  flex-shrink: 0;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.mobile-tabs {
  display: none;
  background: #BBBDA7;
  border-bottom: 1px solid #A8AB96;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.mobile-tabs::-webkit-scrollbar {
  display: none;
}

.tab-button {
  flex: 1;
  min-width: 120px;
  padding: 16px 8px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  position: relative;
}

.tab-button i {
  font-size: 18px;
  margin-bottom: 2px;
}

.tab-button.active {
  color: #FFFFFF;
  background: rgba(255, 255, 255, 0.1);
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #FFFFFF;
  border-radius: 3px 3px 0 0;
}

.mobile-content {
  padding: 24px 16px;
}

.mobile-section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  color: #163053;
}

.mobile-section-header i {
  font-size: 24px;
  color: #A80038;
}

.mobile-section-header h2 {
  font-size: 22px;
  font-weight: 600;
  margin: 0;
}

@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
    gap: 0;
    min-height: auto;
  }
  
  .mobile-tabs {
    display: flex;
    order: 0;
  }
  
  .left-column {
    padding: 0;
    order: 1;
  }
  
  .right-column {
    display: none;
  }
}

.posts-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.post-card {
  background-color: #d7dac1;
  border-radius: 16px;
  padding: 0;
  max-width: 600px;
  width: 90%;
  box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  transition: all 0.3s ease;
}

@media (max-width: 768px) {
  .posts-container {
    padding: 16px;
    gap: 16px;
  }
  
  .post-card {
    width: 100%;
    max-width: none;
    border-radius: 12px;
  }
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0px 12px 32px rgba(0, 0, 0, 0.16);
}

.post-header {
  background-color: #BBBDA7;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.post-title-section {
  flex: 1;
  min-width: 0;
}

.post-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #FFFFFF;
  margin: 0 0 8px 0;
  line-height: 1.4;
  word-wrap: break-word;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.post-date {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.post-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .post-header {
    padding: 16px;
    gap: 12px;
  }
  
  .post-title {
    font-size: 1.1rem;
  }
  
  .post-date {
    font-size: 0.8rem;
  }
  
  .post-actions {
    gap: 6px;
  }
  
  .action-btn {
    padding: 6px;
  }
}

.action-btn {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.action-btn .v-icon {
  color: #FFFFFF;
}

.action-btn i {
  color: #E0E0E0;
  font-size: 16px;
  transition: color 0.2s ease;
}

.post-content {
  padding: 24px;
}

.post-description {
  background-color: #EEF1DC;
  border-radius: 12px;
  padding: 20px;
  font-size: 1rem;
  color: #333333;
  line-height: 1.6;
  white-space: pre-line;
  font-weight: 400;
  border-left: 4px solid #BBBDA7;
  margin-bottom: 16px;
  box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
  .post-content {
    padding: 16px;
  }
  
  .post-description {
    padding: 16px;
    font-size: 0.95rem;
    margin-bottom: 12px;
    border-radius: 8px;
  }
  
  .mobile-content {
    padding: 20px 16px;
  }
}

.post-image-container {
  margin-top: 16px;
  border-radius: 12px;
  overflow: hidden;
  background-color: #F5F5F5;
  border: 1px solid #E0E0E0;
}

.post-image-container :deep(.n-image) {
  display: block;
  width: 100%;
  transition: transform 0.3s ease;
}

.post-image-container :deep(.n-image img) {
  display: block;
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: cover;
  border-radius: 12px;
}

.post-image-container:hover :deep(.n-image img) {
  transform: scale(1.02);
}

.logo-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
}

.birthday-list, .recognition-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.birthday-item {
  background: #EEF1DC;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #A80038;
}

.birthday-emoji {
  font-size: 24px;
}

.birthday-name {
  font-size: 16px;
  font-weight: 500;
  color: #163053;
}

.recognition-item {
  background: #EEF1DC;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #A80038;
}

.recognition-trophy {
  font-size: 24px;
  flex-shrink: 0;
}

.recognition-info {
  flex: 1;
}

.recognition-name {
  font-size: 16px;
  font-weight: 600;
  color: #163053;
  margin-bottom: 4px;
}

.recognition-description {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #888;
}

.empty-state p {
  font-size: 16px;
  margin: 0;
}

.floating-action-buttons {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

.floating-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.floating-btn:hover {
  transform: scale(1.1) translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.floating-btn:active {
  transform: scale(0.95);
}

.floating-btn-post {
  background: linear-gradient(135deg, #A80038, #d32f2f);
}

.floating-btn-post:hover {
  background: linear-gradient(135deg, #d32f2f, #A80038);
}

.floating-btn-recognition {
  background: linear-gradient(135deg, #ff9800, #f57c00);
}

.floating-btn-recognition:hover {
  background: linear-gradient(135deg, #f57c00, #ff9800);
}

@media (min-width: 769px) {
  .floating-action-buttons {
    display: none;
  }
}

@media (max-width: 768px) {
  .logo-image {
    max-width: 200px;
    margin: 0 auto;
  }
}
</style>
