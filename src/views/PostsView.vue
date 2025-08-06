<template>
  <div class="main-container">
    <div class="left-column">
      <ModalPublicacion
        v-model="modalStore.mostrarModalPublicacion"
        :mode="false"
        @agregarPublicacion="agregarPublicacion"
      />
      <div class="posts-container">
        <div class="post-card" v-for="post in posts" :key="post.id">
          <div class="post-date">{{ dateFormatV1(post.fecha_publicacion) }}</div>
          <div class="post-text">{{ post.descripcion }}</div>
          <img v-if="post.imagen" :src="post.imagen" alt="Imagen del anuncio" class="post-image" />
        </div>
      </div>
    </div>
    
    <div class="right-column">
      <n-image width="100%" :src="logo" />
      <CelebrationCard />
    </div>
  </div>
</template>

<script setup>
import AnunciosService from '@/services/AnunciosService'
import { dateFormatV1 } from '@/util/functions.js'
import { ref, onMounted } from 'vue'
import LoginService from '@/services/LoginService'
import ModalPublicacion from './modal/ModalPublicacion.vue'
import logo from '@/assets/OGBU-logo.png'
import CelebrationCard from '@/components/layout/CelebrationCard.vue'
import { modalStore } from '@/stores/modalStore'

const isAdmin = LoginService.isAdmin()
const posts = ref([])

async function loadPublicaciones() {
  try {
    posts.value = await AnunciosService.listarAnuncios()
  } catch (error) {
    console.error('Error al obtener anuncios:', error)
  }
}

function agregarPublicacion(pub) {
  posts.value.unshift(pub)
}

onMounted(() => {
  loadPublicaciones()
})
</script>


<style scoped>
.main-container {
  display: flex;
  gap: 20px;
  height: 100vh;
  overflow: hidden;
}

.left-column {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* Internet Explorer y Edge */
}

.left-column::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.right-column {
  width: 347px;
  flex-shrink: 0;
  padding: 32px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.posts-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}
.post-card {
  background-color: #BBBDA7;
  border-radius: 15px;
  padding: 15px;
  max-width: 600px;
  width: 90%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.post-date {
  font-size: 0.9rem;
  color: white;
  margin-bottom: 8px;
}
.post-text {
   background-color: #EAEBDF;
  border-radius: 15px;
  padding: 15px;
  max-width: 600px;
  width: 100%;
  font-size: 1rem;
  color: #333;
  margin-bottom: 10px;
  white-space: pre-line;
  font-weight: normal;
}
.post-image {
  display: block;
  margin: 0 auto;
  width: 100%;
  max-width: 450px;
  border-radius: 10px;
  margin-top: 10px;
}
</style>
