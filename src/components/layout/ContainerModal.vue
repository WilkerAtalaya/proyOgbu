<template>
  <v-dialog v-model="dialog" :max-width="maxWidth" persistent scrollable>
    <v-card style="border-radius: 16px; padding: 32px 45px 36px; position: relative;">
        <button
          @click="dialog = false"
          class="close-button"
          :style="{ color: colorTheme }"
          title="Cerrar Modal"
        >
          <i class="fa-solid fa-xmark" style="font-size: 20px"></i>
        </button>
        <v-card-title class="pa-0 mb-4">
            <h2 :style="{ color: colorTheme, textAlign: 'center', width: '100%', fontSize: '35px', fontWeight: 400, fontFamily: 'Righteous, cursive' }">{{ title }}</h2>
        </v-card-title>
        <v-card-text style="max-height: 70vh; overflow-y: auto;">
          <slot />
        </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  maxWidth: {
    type: Number,
    default: 600
  },
  colorTheme: {
    type: String,
    default: '32px 60px'
  },
  title: {
    type: String,
    default: 'Modal Title'
  },
})

const emit = defineEmits(['update:modelValue'])

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})
</script>

<style scoped>
.close-button {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  cursor: pointer;
  z-index: 10;
  transition: opacity 0.2s ease;
}

.close-button:hover {
  opacity: 0.7;
}
</style>
