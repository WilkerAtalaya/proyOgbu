<template>
  <n-button class="btn-action">
    <div style="display: flex; align-items: center; gap: 5px">{{ label }}</div>
  </n-button>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
})
</script>

<style scoped>
.btn-action {
  background-color: #53696d;
  padding: 20px;
  color: white;
  width: 100%;
  border-radius: 10px;
}
.icon-green {
  color: green;
}
.icon-red {
  color: red;
}
</style>
