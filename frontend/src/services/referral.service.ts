import { api } from "@/api/instance.api";
import { userService } from "@/services/user.service";
import { Referral } from "@/types/referral.interface";

class ReferralService {
    public async getUserReferrals() {
        try {
            const telegram_id = (await userService.getUser()).telegram_id;
            const response = await api.get<Referral>(`referral_tree/${telegram_id}`);
            return response;
        } catch (error) {
            throw error;
        }
    }
}

export const referralService = new ReferralService()