import React from "react";
import { toast } from "react-hot-toast";
import CustomToast from "../components/ui/CustomToast";

export const notify = {
  success: (message: string) => {
    toast.custom((t) => <CustomToast t={t} message={message} type="success" />);
  },
  error: (message: string) => {
    toast.custom((t) => <CustomToast t={t} message={message} type="error" />);
  },
  info: (message: string) => {
    toast.custom((t) => <CustomToast t={t} message={message} type="info" />);
  },
  loading: (message: string) => {
    return toast.custom((t) => (
      <CustomToast t={t} message={message} type="loading" />
    ));
  },
  dismiss: (toastId?: string) => {
    toast.dismiss(toastId);
  },
};
