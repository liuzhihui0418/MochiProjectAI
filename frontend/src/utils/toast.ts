// src/utils/toast.ts
import { ref } from 'vue';

// 定义通知类型
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: number;
  type: ToastType;
  title: string;
  message?: string;
}

// 响应式数据源
const toasts = ref<ToastMessage[]>([]);

// 自动递增ID
let idCounter = 0;

export const useToast = () => {
  // 添加通知
  const add = (title: string, type: ToastType = 'info', message: string = '', duration: number = 3000) => {
    const id = idCounter++;
    const newToast = { id, type, title, message };

    // 限制最大显示数量，防止刷屏
    if (toasts.value.length >= 5) {
      toasts.value.shift();
    }

    toasts.value.push(newToast);

    // 自动移除
    if (duration > 0) {
      setTimeout(() => {
        remove(id);
      }, duration);
    }
  };

  // 移除通知
  const remove = (id: number) => {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  };

  // 快捷方法
  const success = (title: string, msg?: string) => add(title, 'success', msg);
  const error = (title: string, msg?: string) => add(title, 'error', msg, 5000); // 错误多停留一会
  const warning = (title: string, msg?: string) => add(title, 'warning', msg);
  const info = (title: string, msg?: string) => add(title, 'info', msg);

  return { toasts, add, remove, success, error, warning, info };
};