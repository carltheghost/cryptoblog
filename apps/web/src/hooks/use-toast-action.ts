import { toast } from "sonner";

export async function toastAction<T>(
  action: () => Promise<T>,
  messages: { loading?: string; success: string | ((data: T) => string); error?: string }
): Promise<T | null> {
  const id = messages.loading ? toast.loading(messages.loading) : undefined;
  try {
    const result = await action();
    const successMsg = typeof messages.success === "function" ? messages.success(result) : messages.success;
    if (id) toast.success(successMsg, { id });
    else toast.success(successMsg);
    return result;
  } catch (e) {
    const msg = e instanceof Error ? e.message : messages.error || "Something went wrong";
    if (id) toast.error(msg, { id });
    else toast.error(msg);
    return null;
  }
}
