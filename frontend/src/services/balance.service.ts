

import { api } from "@/api/instance.api";
import { userService } from "@/services/user.service";
import { Balance, Investments, TopupMainBalance, TranferToTradingBalance, Transaction } from "@/types/balance.interface";
import { toast } from "sonner";

class BalanceService {
    public async getUserBalance() {
        try {
            const telegram_id = (await userService.getUser()).telegram_id;
            const response = await api.get<Balance>(`balance/${telegram_id}`);
            return response;
        } catch (error) {
            throw error;
        }
    }

    public async transferToTrading(amount: number) {
        try {
            const telegram_id = (await userService.getUser()).telegram_id;
            const response = await api.post<TranferToTradingBalance>(`transfer_to_trading/${telegram_id}`, {
                "amount": amount
            });
            toast("Баланс успешно пополнен");
            return response;
        } catch (error: any) {
            toast(error.toString());
        }
    }

    public async transferToMain(amount: number) {
        try {
            const telegram_id = (await userService.getUser()).telegram_id;
            const response = await api.post<TranferToTradingBalance>(`transfer_to_main/${telegram_id}`, {
                "amount": amount
            });
            toast("Перевод успешно выполнен");
            return response;
        } catch (error: any) {
            toast(error.toString());
        }
    }

    public async topupMainBalance(amount: number) {
        try {
            const telegram_id = (await userService.getUser()).telegram_id;
            const response = await api.post<TopupMainBalance>(`deposit/${telegram_id}`, {
                "amount": amount
            });
            toast("Вы успешно пополнили баланс");
            return response;
        } catch (error: any) {
            console.log(error)
            toast(error.toString());
        }
    }

    public async transactions() {
        try {
            const telegram_id = (await userService.getUser()).telegram_id;
            const response = await api.get<Transaction[]>(`transactions/${telegram_id}`);
            return response;
        } catch (error) {
            throw error;
        }
    }


    public async investments() {
        try {
            const telegram_id = (await userService.getUser()).telegram_id;
            const response = await api.get<Investments>(`signals/investments/${telegram_id}`);
            return response;
        } catch (error) {
            throw error;
        }
    }
}

export const balanceService = new BalanceService()