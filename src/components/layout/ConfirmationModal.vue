<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card class="confirmation-modal">
      <v-card-title class="modal-header">
        <i :class="icon" :style="{ color: iconColor, fontSize: '32px' }" class="mr-3"></i>
        <span class="modal-title">{{ title }}</span>
      </v-card-title>
      
      <v-card-text class="modal-content">
        <p class="modal-message">{{ message }}</p>
      </v-card-text>
      
      <v-card-actions class="modal-actions">
        <v-spacer></v-spacer>
        <v-btn
          variant="outlined"
          @click="handleCancel"
          class="cancel-btn"
        >
          {{ cancelText }}
        </v-btn>
        <v-btn
          :color="confirmColor"
          @click="handleConfirm"
          class="confirm-btn"
        >
          {{ confirmText }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  title: {
    type: String,
    default: 'Confirmar acción'
  },
  message: {
    type: String,
    default: '¿Estás seguro de que deseas continuar?'
  },
  confirmText: {
    type: String,
    default: 'Confirmar'
  },
  cancelText: {
    type: String,
    default: 'Cancelar'
  },
  confirmColor: {
    type: String,
    default: '#A80038'
  },
  icon: {
    type: String,
    default: 'fas fa-question-circle'
  },
  iconColor: {
    type: String,
    default: '#F2B200'
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

function handleConfirm() {
  emit('confirm')
  dialog.value = false
}

function handleCancel() {
  emit('cancel')
  dialog.value = false
}
</script>

<style scoped>
.confirmation-modal {
  border-radius: 16px;
  overflow: hidden;
}

.modal-header {
  background-color: #f8f9fa;
  padding: 24px;
  border-bottom: 1px solid #e9ecef;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
}

.modal-content {
  padding: 24px;
}

.modal-message {
  font-size: 1rem;
  color: #555;
  line-height: 1.5;
  margin: 0;
}

.modal-actions {
  padding: 16px 24px 24px;
  gap: 12px;
}

.cancel-btn {
  border-color: #6c757d;
  color: #6c757d;
}

.cancel-btn:hover {
  background-color: #f8f9fa;
}

.confirm-btn {
  font-weight: 500;
}
</style>
