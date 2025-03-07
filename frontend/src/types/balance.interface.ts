export interface Balance {
    id: number
    telegram_id: number
    balance: number
    trade_balance: number
    frozen_balance: number
}

export type TranferToTradingBalance = {
    amount: number
}

export type TopupMainBalance = {
    amount: number
}

export interface Transaction {
    id: number
    amount: number
    transaction_type: string
    created_at: Date
}

interface Investment {
    id: number,
    signal_id: number,
    amount: number,
    profit: number,
    created_at: Date
}

export interface Investments {
    user_id: number
    investments: Investment[]
}