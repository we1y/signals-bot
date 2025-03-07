import { api } from "@/api/instance.api";
import { User } from "@/types/user.interface";
import { getUserAuthToken } from "./auth.service";

class UserService {
    public async getUser() {
        try {
            const token = await getUserAuthToken();
            const response = await api.get<User>(`api/auth?token=${token}`);
            return response;
        } catch (error) {
            throw error;
        }
    }

    public async findUserById(telegram_id: number) {
        try {
            const response = await api.get<User>(`user/${telegram_id}`);
            return response;
        } catch (error) {
            throw error;
        }
    }

    public async findUserByUsername(telegram_username: string) {
        try {
            const response = await api.get<User>(`user/${telegram_username}`);
            return response;
        } catch (error) {
            throw error;
        }
    }
}

export const userService = new UserService()