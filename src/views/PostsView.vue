<template>
  <div class="main-container">
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
      <div class="posts-container">
        <div class="post-card" v-for="post in posts" :key="post.id">
          <div class="post-header">
            <div class="post-title-section">
              <h3 class="post-title">{{ post.titulo }}</h3>
              <div class="post-meta">
                <span class="post-date">{{ dateFormatV1(post.fecha_publicacion) }}</span>
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
            <div v-if="post.imagen" class="post-image-container">
              <n-image 
                :src="post.imagen" 
                alt="Imagen del anuncio"
                object-fit="cover"
                :style="{ width: '100%', height: 'auto', maxHeight: '400px', borderRadius: '12px' }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="right-column">
      <img :src="logo" alt="Logo OGBU" class="logo-image" />
      <CelebrationCard />
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
import { dateFormatV1 } from '@/util/functions.js'
import { ref, onMounted } from 'vue'
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

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
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
  editingPost.value = null
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

onMounted(() => {
  loadPublicaciones()
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
</style>
