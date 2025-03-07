

import { api } from "@/api/instance.api";
import { ActiveSignals, CustomSignal, JoinSignal, RandomSignal } from "@/types/signal.interface";
import { toast } from "sonner";

class SignalService {
    public async joinSignal(telegram_id: number, signal_id: number, amount: number) {
        try {
            const response = await api.post<JoinSignal>('signals/join', {
                "telegram_id": telegram_id,
                "signal_id": signal_id,
                "amount": amount
            });
            toast("Вы успешно вошли в сигнал");
            return response;
        } catch (error: any) {
            toast(error.toString());
        }
    }

    public async createCustomSignal(name: string, joinTime: number, activeTime: number, burnChance: number, profitPercent: number) {
        try {
            const response = await api.post<CustomSignal>('signals/create_custom', {
                "name": name,
                "join_time": joinTime,
                "active_time": activeTime,
                "burn_chance": burnChance,
                "profit_percent": profitPercent
            });
            return response;
        } catch (error) {
            throw error;
        }
    }

    public async createRandomSignal(name: string) {
        try {
            const response = await api.post<RandomSignal>('signals/create_random', {
                "name": name
            });
            return response;
        } catch (error) {
            throw error;
        }
    }

    public async activeSignals() {
        try {
            const response = await api.get<ActiveSignals>('signals/active');
            return response;
        } catch (error) {
            throw error;
        }
    }
}

export const signalService = new SignalService()