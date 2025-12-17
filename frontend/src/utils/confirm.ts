import { ref } from 'vue';

interface ConfirmOptions {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'warning' | 'info' | 'danger';
}

// 响应式状态
const visible = ref(false);
const state = ref<ConfirmOptions>({
  title: '',
  message: '',
  type: 'warning'
});

// 存储 Promise 的 resolve 函数
let resolvePromise: (value: boolean) => void;

export const useConfirm = () => {
  // 核心方法：调用它会返回一个 Promise<boolean>
  const confirm = (message: string, title: string = '操作确认', type: 'warning' | 'info' | 'danger' = 'warning') => {
    state.value = { title, message, type };
    visible.value = true;

    return new Promise<boolean>((resolve) => {
      resolvePromise = resolve;
    });
  };

  // 用户点击确定
  const handleConfirm = () => {
    visible.value = false;
    if (resolvePromise) resolvePromise(true);
  };

  // 用户点击取消
  const handleCancel = () => {
    visible.value = false;
    if (resolvePromise) resolvePromise(false);
  };

  return {
    visible,
    state,
    confirm,
    handleConfirm,
    handleCancel
  };
};