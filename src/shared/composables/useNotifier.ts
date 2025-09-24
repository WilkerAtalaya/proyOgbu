import { ref } from 'vue';
import { NotificationType } from '../enums/notification.enum';

export const snackbar = ref(false);
export const message = ref('');
export const color = ref<NotificationType>(NotificationType.INFO);

export function useNotifier() {
  function notify(
    msg: string | { message: string },
    type: NotificationType = NotificationType.INFO,
  ) {
    let finalMessage = 'Ocurrió un error';

    if (typeof msg === 'string') {
      finalMessage = msg;
    } else if (typeof msg === 'object' && msg?.message) {
      finalMessage = msg.message;
    }

    message.value = finalMessage;
    color.value = type;
    snackbar.value = true;
  }

  return { notify };
}

export const notify = useNotifier().notify;
