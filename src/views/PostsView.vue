<template>
  <div v-if="isAdmin" style="margin-bottom: 16px">
    <n-button type="primary" @click="mostrarModal = true">Crear publicación</n-button>
  </div>
  <n-modal v-model:show="mostrarModal" title="Nueva Publicación">
    <div style="display: flex; flex-direction: column; gap: 12px; padding: 16px">
      <n-input
        v-model:value="nuevaPublicacion.descripcion"
        placeholder="Descripción de la publicación"
        type="textarea"
      />
      <n-upload
        :max="1"
        :custom-request="subirImagen"
        :show-file-list="false"
        accept="image/*"
      >
        <n-button>Subir Imagen</n-button>
      </n-upload>
      <n-button type="primary" @click="enviarPublicacion">Enviar</n-button>
    </div>
  </n-modal>
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
const isAdmin = LoginService.isAdmin()
export default {
  name: 'PostsView',
  data() {
    return {
      isAdmin,
      posts: [],
      dateFormatV1,
      mostrarModal: ref(false),
      nuevaPublicacion: ref({
        descripcion: '',
        imagen: ''
      })
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
    async enviarPublicacion() {
      const user = LoginService.getCurrentUser()
      const formData = new FormData()
      formData.append('id_usuario', user.id.toString())
      formData.append('descripcion', this.nuevaPublicacion.descripcion)
      formData.append('imagen', this.nuevaPublicacion.imagen)
      await AnunciosService.crearAnuncio(formData)
      this.posts.unshift({ 
        id_usuario: user.id,
        descripcion: this.nuevaPublicacion.descripcion,
        imagen: this.nuevaPublicacion.imagen,
        fecha_publicacion: new Date()
      })
      this.nuevaPublicacion = { descripcion: '', imagen: '' }
      this.mostrarModal = false
    }
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
