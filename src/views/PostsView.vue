<template>
  <div v-if="isAdmin" style="margin-bottom: 16px;" class="text-right pr-4">
    <button style="background-color: #b28700; color:aliceblue; border-radius: 8px; padding: 8px 20px; border: none; font-weight: 500; cursor: pointer" @click="mostrarModal = true">Crear publicación</button>
  </div>
  <ModalPublicacion
    v-model="mostrarModal"
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
</template>

<script>
import AnunciosService from '@/services/AnunciosService'
import { dateFormatV1 } from '@/util/functions.js'
import { ref } from 'vue'
import LoginService from '@/services/LoginService'
import ModalPublicacion from './modal/ModalPublicacion.vue'

const isAdmin = LoginService.isAdmin()

export default {
  name: 'PostsView',
  components: { ModalPublicacion },
  data() {
    return {
      isAdmin,
      posts: [],
      dateFormatV1,
      mostrarModal: false,
    }
  },
  methods: {
    async loadPublicaciones() {
      try {
        this.posts = await AnunciosService.listarAnuncios()
      } catch (error) {
        console.error('Error al obtener anuncios:', error)
      }
    },
    agregarPublicacion(pub) {
      this.posts.unshift(pub)
    },
  },
  mounted() {
    this.loadPublicaciones()
  },
}
</script>


<style scoped>
.posts-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}
.post-card {
  background-color: #eaf0e6;
  border-radius: 15px;
  padding: 15px;
  max-width: 600px;
  width: 90%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.post-date {
  font-size: 0.9rem;
  color: #686868;
  margin-bottom: 8px;
}
.post-text {
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
