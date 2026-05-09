import apiClient from "./apiClient";
import { User } from "../types/auth";

const userService = {
  /**
   * Uploads an avatar image for the current user.
   * @param file The image file to upload.
   */
  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post<{ avatar_url: string }>(
      "/users/me/avatar",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  /**
   * Updates user information (can be extended).
   * @param userData Updated user information.
   */
  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>("/users/me", userData);
    return response.data;
  },
};

export default userService;
