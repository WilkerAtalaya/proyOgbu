<template>
  <n-card class="user-card">
    <div style="display: flex; align-items: center; gap: 16px">
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
  padding: 16px 20px;
  border-radius: 25px;
  box-shadow: 0px 10px 4px 0px #00000040;
  border: none;
}
.user-card p {
  margin: 0;
  color: white;
  font-size: 20px;
  font-weight: 400;
}
.icon-green {
  color: green;
  font-size: 16px;
}
</style>
