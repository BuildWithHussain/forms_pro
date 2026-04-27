import { reactive } from "vue";

export interface DialogAction {
  label: string;
  variant?: "solid" | "outline" | "ghost" | "subtle";
  theme?: "red" | "blue" | "green" | "gray";
  onClick?: () => void | Promise<void>;
}

export interface DialogOptions {
  title: string;
  message: string;
  actions?: DialogAction[];
}

export interface DialogState {
  open: boolean;
  title: string;
  message: string;
  actions: DialogAction[];
  resolve: ((value: boolean) => void) | null;
}

export const dialogState = reactive<DialogState>({
  open: false,
  title: "",
  message: "",
  actions: [],
  resolve: null,
});

function closeDialog(result: boolean = false) {
  dialogState.open = false;
  if (dialogState.resolve) {
    dialogState.resolve(result);
    dialogState.resolve = null;
  }
}

export const dialog = {
  show(options: DialogOptions): Promise<boolean> {
    return new Promise((resolve) => {
      dialogState.title = options.title;
      dialogState.message = options.message;
      dialogState.actions = options.actions || [
        { label: "OK", variant: "solid" },
      ];
      dialogState.resolve = resolve;
      dialogState.open = true;
    });
  },

  confirm(options: Omit<DialogOptions, "actions">): Promise<boolean> {
    return this.show({
      ...options,
      actions: [
        {
          label: "Cancel",
          variant: "outline",
          onClick: () => closeDialog(false),
        },
        {
          label: "Confirm",
          variant: "solid",
          onClick: () => closeDialog(true),
        },
      ],
    });
  },

  alert(options: Omit<DialogOptions, "actions">): Promise<boolean> {
    return this.show({
      ...options,
      actions: [
        {
          label: "OK",
          variant: "solid",
          onClick: () => closeDialog(true),
        },
      ],
    });
  },

  close: closeDialog,
};
