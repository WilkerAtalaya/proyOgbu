<template>
  <n-card class="card-sidemenu">
    <n-menu :options="menuOptions" :value="route.path" @update:value="navigate" />
  </n-card>
</template>

<script setup>
import { ref } from 'vue'
import { h } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const selectedKey = ref(route.path)

const menuOptions = [
  {
    label: 'Anuncios',
    key: '/anuncios',
    icon: () =>
      h('i', { class: 'fa-solid fa-bullhorn', style: 'color: white; margin-right: 4px;' }),
  },
  {
    label: 'Quejas',
    key: '/quejas',
    icon: () =>
      h('i', { class: 'fa-regular fa-clipboard', style: 'color: white; margin-right: 4px;' }),
  },
  {
    label: 'Actividades',
    key: '/actividades',
    icon: () =>
      h('i', { class: 'fa-solid fa-person-running', style: 'color: white; margin-right: 4px;' }),
  },
  {
    label: 'Permisos',
    key: '/permisos',
    icon: () =>
      h('i', {
        class: 'fa-solid fa-person-circle-check',
        style: 'color: white; margin-right: 4px;',
      }),
  },
  {
    label: 'Citas',
    key: '/citas',
    icon: () =>
      h('i', { class: 'fa-regular fa-calendar-days', style: 'color: white; margin-right: 4px;' }),
  },
  {
    label: 'Asistencia',
    key: '/asistencia',
    icon: () =>
      h('i', { class: 'fa-regular fa-calendar-check', style: 'color: white; margin-right: 4px;' }),
  },
]

function navigate(key) {
  router.push(key)
}
</script>

<style scoped>
.card-sidemenu {
  background-color: #7e271b;
  width: 100%;
  padding: 10px;
  border-radius: 25px;
  border: none;
}
</style>
