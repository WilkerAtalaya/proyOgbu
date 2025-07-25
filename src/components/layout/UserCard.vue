<template>
  <n-card class="user-card">
    <div style="display: flex; align-items: center; gap: 5px">
      <i class="fa-solid fa-circle icon-green"></i>
      <p>{{ props.user?.nombre }}</p>
    </div>
  </n-card>
 
</template>
<script setup>
const props = defineProps({
  user: Object
})
</script>
<style scoped>
.user-card {
  background-color: #373b41;
  padding: 15px;
  color: white;
  border-radius: 20px;
}
.icon-green {
  color: green;
}
.icon-red {
  color: red;
}
</style>
